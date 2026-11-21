"""Men Tarmoq lab-agent — home serverda (alohida VM ichida) ishlaydi.

Vazifasi: platformadan (VPS, WireGuard orqali) kelgan buyruq bo'yicha
containerlab topologiyalarini har bir talaba uchun alohida ko'tarish,
brauzer-terminal (ttyd) konteynerini Traefik orqali /term/<id>/ ga chiqarish,
topshiriqlarni avtomatik tekshirish va muddati o'tgan lablarni tozalash.

Xavfsizlik: agent hech qachon tarmoqdan kelgan buyruqni bajarmaydi —
tekshiruv buyruqlari faqat labs/<topologiya>/lab.yaml dan o'qiladi.
"""
from __future__ import annotations

import asyncio
import hmac
import ipaddress
import json
import logging
import os
import re
import shutil
import time
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from typing import Any

import yaml
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

log = logging.getLogger("lab-agent")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

ID_RE = re.compile(r"^[a-z0-9]{6,32}$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
NODE_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,40}$")
SHELL_RE = re.compile(r"^[a-z0-9/_-]{1,40}$")


class Config:
    def __init__(self) -> None:
        self.token = os.getenv("AGENT_TOKEN", "")
        self.labs_dir = Path(os.getenv("LABS_DIR", Path(__file__).resolve().parents[2] / "labs")).resolve()
        self.work_dir = Path(os.getenv("WORK_DIR", "/var/lib/men-tarmoq/labs"))
        self.max_labs = int(os.getenv("MAX_LABS", "8"))
        self.max_ttl = int(os.getenv("MAX_TTL_MINUTES", "240"))
        self.mgmt_pool = ipaddress.ip_network(os.getenv("MGMT_POOL", "172.31.0.0/16"))
        self.term_image = os.getenv("TERM_IMAGE", "men-tarmoq/term:latest")
        self.term_network = os.getenv("TERM_NETWORK", "labterm")
        self.term_base = os.getenv("TERM_BASE_PATH", "/term").rstrip("/")
        self.clab = os.getenv("CLAB_BIN", "containerlab")
        self.docker = os.getenv("DOCKER_BIN", "docker")
        self.node_memory = os.getenv("NODE_MEMORY", "512MB")
        self.node_cpu = os.getenv("NODE_CPU", "1")
        self.deploy_timeout = int(os.getenv("DEPLOY_TIMEOUT", "900"))


cfg = Config()


# ---------------------------------------------------------------- process runner
async def run(*cmd: str, timeout: float = 60) -> tuple[int, str]:
    """Buyruqni shell'siz (argv) bajaradi — injection imkoniyati yo'q."""
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        with suppress(ProcessLookupError):
            proc.kill()
        return 124, f"timeout ({timeout}s): {' '.join(cmd[:3])}"
    return proc.returncode or 0, out.decode(errors="replace")


# ---------------------------------------------------------------- lab definitions
def load_labdef(topology: str) -> dict[str, Any]:
    if not SLUG_RE.match(topology):
        raise HTTPException(400, "noto'g'ri topologiya nomi")
    ldir = cfg.labs_dir / topology
    if not (ldir / "lab.yaml").is_file() or not (ldir / "topology.clab.yml").is_file():
        raise HTTPException(404, f"topologiya topilmadi: {topology}")
    data = yaml.safe_load((ldir / "lab.yaml").read_text(encoding="utf-8")) or {}
    for n in data.get("nodes", []):
        if not NODE_RE.match(str(n.get("name", ""))) or not SHELL_RE.match(str(n.get("shell", "sh"))):
            raise HTTPException(500, f"lab.yaml da noto'g'ri tugun: {n}")
    return data


def clab_name(lab_id: str) -> str:
    return f"mt{lab_id}"


def subnet_for(index: int) -> tuple[str, str]:
    v4 = list(cfg.mgmt_pool.subnets(new_prefix=24))[index]
    v6 = f"fd6d:7400:0:{index:x}::/64"
    return str(v4), v6


def render_topology(src: Path, lab_id: str, index: int) -> dict[str, Any]:
    """Topologiyani har bir talaba uchun izolyatsiya qiladi: nom, mgmt tarmog'i, resurs limitlari."""
    topo = yaml.safe_load(src.read_text(encoding="utf-8")) or {}
    v4, v6 = subnet_for(index)
    topo["name"] = clab_name(lab_id)
    topo["prefix"] = "clab"
    topo["mgmt"] = {"network": f"mt-{lab_id}", "ipv4-subnet": v4, "ipv6-subnet": v6}
    defaults = topo.setdefault("topology", {}).setdefault("defaults", {})
    defaults.setdefault("memory", cfg.node_memory)
    defaults.setdefault("cpu", float(cfg.node_cpu))
    return topo


def container_name(lab_id: str, node: str) -> str:
    return f"clab-{clab_name(lab_id)}-{node}"


# ---------------------------------------------------------------- state
class State:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.labs: dict[str, dict[str, Any]] = {}
        self.lock = asyncio.Lock()
        if path.is_file():
            with suppress(ValueError, OSError):
                self.labs = json.loads(path.read_text())

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.labs, indent=2))
        tmp.replace(self.path)

    def free_index(self) -> int:
        used = {lab["index"] for lab in self.labs.values()}
        total = 2 ** (24 - cfg.mgmt_pool.prefixlen)
        for i in range(total):
            if i not in used:
                return i
        raise HTTPException(503, "mgmt subnet pool tugadi")


state: State | None = None


def get_state() -> State:
    assert state is not None
    return state


# ---------------------------------------------------------------- lifecycle
async def deploy(lab_id: str) -> None:
    st = get_state()
    lab = st.labs[lab_id]
    work = cfg.work_dir / lab_id
    try:
        src = cfg.labs_dir / lab["topology"]
        if work.exists():
            shutil.rmtree(work)
        shutil.copytree(src, work)
        topo_file = work / "topology.clab.yml"
        topo_file.write_text(yaml.safe_dump(render_topology(src / "topology.clab.yml", lab_id, lab["index"]), sort_keys=False))

        rc, out = await run(cfg.clab, "deploy", "-t", str(topo_file), "--reconfigure", timeout=cfg.deploy_timeout)
        if rc != 0:
            raise RuntimeError(f"containerlab deploy xatosi: {out[-400:]}")

        labdef = load_labdef(lab["topology"])
        specs = [f"{n['name']}:{n.get('shell', 'sh')}" for n in labdef.get("nodes", [])]
        base = f"{cfg.term_base}/{lab_id}"
        router = f"mt-term-{lab_id}"
        await run(cfg.docker, "rm", "-f", router)
        rc, out = await run(
            cfg.docker, "run", "-d", "--name", router,
            "--network", cfg.term_network,
            "--memory", "128m", "--pids-limit", "128",
            "--restart", "unless-stopped",
            "-v", "/var/run/docker.sock:/var/run/docker.sock",
            "--label", "men-tarmoq.lab=" + lab_id,
            "--label", "traefik.enable=true",
            "--label", f"traefik.docker.network={cfg.term_network}",
            "--label", f"traefik.http.routers.{router}.rule=PathPrefix(`{base}`)",
            "--label", f"traefik.http.routers.{router}.entrypoints=web",
            "--label", f"traefik.http.services.{router}.loadbalancer.server.port=7681",
            cfg.term_image,
            "ttyd", "-W", "-p", "7681", "-m", "3", "-b", base,
            "-t", "titleFixed=Men Tarmoq Lab", "-t", "fontSize=15",
            "lab-shell", clab_name(lab_id), *specs,
            timeout=120,
        )
        if rc != 0:
            raise RuntimeError(f"terminal konteyneri xatosi: {out[-300:]}")
        async with st.lock:
            if lab_id in st.labs:
                st.labs[lab_id].update(status="running", message=None)
                st.save()
        log.info("Lab %s (%s) tayyor", lab_id, lab["topology"])
    except Exception as exc:  # noqa: BLE001
        log.exception("Lab %s deploy muvaffaqiyatsiz", lab_id)
        async with st.lock:
            if lab_id in st.labs:
                st.labs[lab_id].update(status="error", message=str(exc)[:480])
                st.save()


async def teardown(lab_id: str) -> None:
    st = get_state()
    work = cfg.work_dir / lab_id
    await run(cfg.docker, "rm", "-f", f"mt-term-{lab_id}")
    topo_file = work / "topology.clab.yml"
    if topo_file.is_file():
        rc, out = await run(cfg.clab, "destroy", "-t", str(topo_file), "--cleanup", timeout=300)
        if rc != 0:
            log.warning("Lab %s destroy: %s", lab_id, out[-300:])
    shutil.rmtree(work, ignore_errors=True)
    async with st.lock:
        st.labs.pop(lab_id, None)
        st.save()
    log.info("Lab %s o'chirildi", lab_id)


async def reaper() -> None:
    while True:
        await asyncio.sleep(60)
        now = time.time()
        expired = [lid for lid, lab in list(get_state().labs.items()) if lab["expires_at"] < now]
        for lid in expired:
            log.info("Lab %s muddati tugadi", lid)
            with suppress(Exception):
                await teardown(lid)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global state
    if not cfg.token or len(cfg.token) < 24:
        raise RuntimeError("AGENT_TOKEN o'rnatilmagan yoki juda qisqa (kamida 24 belgi)")
    cfg.work_dir.mkdir(parents=True, exist_ok=True)
    state = State(cfg.work_dir / "state.json")
    task = asyncio.create_task(reaper())
    yield
    task.cancel()


app = FastAPI(title="Men Tarmoq lab-agent", lifespan=lifespan, docs_url=None, redoc_url=None)


def auth(authorization: str = Header("")) -> None:
    expected = f"Bearer {cfg.token}"
    if not cfg.token or not hmac.compare_digest(authorization.encode(), expected.encode()):
        raise HTTPException(401, "unauthorized")


class CreateLab(BaseModel):
    id: str = Field(pattern=ID_RE.pattern)
    topology: str = Field(pattern=SLUG_RE.pattern)
    ttl_minutes: int = Field(default=90, ge=5)


def public(lab_id: str, lab: dict[str, Any]) -> dict[str, Any]:
    return {"id": lab_id, **{k: lab[k] for k in ("topology", "status", "message", "created_at", "expires_at")}}


_clab_version: str | None = None


@app.get("/health", dependencies=[Depends(auth)])
async def health():
    global _clab_version
    if _clab_version is None:
        rc, out = await run(cfg.clab, "version", timeout=10)
        m = re.search(r"version:\s*(\S+)", out)
        _clab_version = m.group(1) if (rc == 0 and m) else "unknown"
    return {"ok": True, "active_labs": len(get_state().labs), "max_labs": cfg.max_labs, "containerlab": _clab_version}


@app.get("/labs", dependencies=[Depends(auth)])
async def list_labs():
    return [public(lid, lab) for lid, lab in get_state().labs.items()]


@app.post("/labs", dependencies=[Depends(auth)], status_code=202)
async def create_lab(body: CreateLab):
    load_labdef(body.topology)  # mavjudligini tekshirish
    st = get_state()
    async with st.lock:
        if body.id in st.labs:
            raise HTTPException(409, "bu id band")
        if len(st.labs) >= cfg.max_labs:
            raise HTTPException(503, "Lab server band — barcha joylar to'lgan. Birozdan keyin urinib ko'ring.")
        now = time.time()
        st.labs[body.id] = {
            "topology": body.topology,
            "status": "provisioning",
            "message": None,
            "index": st.free_index(),
            "created_at": now,
            "expires_at": now + 60 * min(body.ttl_minutes, cfg.max_ttl),
        }
        st.save()
    asyncio.create_task(deploy(body.id))
    return public(body.id, st.labs[body.id])


@app.get("/labs/{lab_id}", dependencies=[Depends(auth)])
async def get_lab(lab_id: str):
    lab = get_state().labs.get(lab_id)
    if not lab:
        raise HTTPException(404, "topilmadi")
    return public(lab_id, lab)


@app.delete("/labs/{lab_id}", dependencies=[Depends(auth)])
async def delete_lab(lab_id: str):
    if not ID_RE.match(lab_id):
        raise HTTPException(400)
    if lab_id not in get_state().labs:
        raise HTTPException(404, "topilmadi")
    await teardown(lab_id)
    return {"ok": True}


@app.post("/labs/{lab_id}/check", dependencies=[Depends(auth)])
async def check_lab(lab_id: str):
    lab = get_state().labs.get(lab_id)
    if not lab:
        raise HTTPException(404, "topilmadi")
    if lab["status"] != "running":
        raise HTTPException(409, "lab hali tayyor emas")
    labdef = load_labdef(lab["topology"])
    node_names = {n["name"] for n in labdef.get("nodes", [])}

    async def one(check: dict[str, Any]) -> dict[str, Any]:
        node = str(check["node"])
        if node not in node_names:
            return {"id": check["id"], "ok": False, "output": "noma'lum tugun"}
        rc, out = await run(cfg.docker, "exec", container_name(lab_id, node), "sh", "-c", str(check["cmd"]), timeout=20)
        ok = re.search(str(check["expect"]), out, re.M) is not None
        return {"id": check["id"], "ok": ok, "output": out[-400:]}

    results = await asyncio.gather(*(one(c) for c in labdef.get("checks", [])))
    return {"results": list(results)}
