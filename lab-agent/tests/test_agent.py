import asyncio
import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
os.environ["AGENT_TOKEN"] = "t" * 32
os.environ["WORK_DIR"] = tempfile.mkdtemp()
os.environ["LABS_DIR"] = str(ROOT.parent / "labs")
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from agent import main  # noqa: E402

AUTH = {"Authorization": "Bearer " + "t" * 32}


@pytest.fixture
def client(monkeypatch):
    calls = []

    async def fake_run(*cmd, timeout=60):
        calls.append(cmd)
        if cmd[:2] == ("docker", "exec"):
            script = cmd[-1]
            if "ip -4 addr" in script:
                return 0, "inet 10.0.12.1/24 brd 10.0.12.255 scope global eth1"
            return 0, "nothing"
        return 0, "ok"

    monkeypatch.setattr(main, "run", fake_run)
    with TestClient(main.app) as c:
        c.calls = calls
        yield c


def test_render_topology_isolates_each_lab():
    src = main.cfg.labs_dir / "ospf-triangle" / "topology.clab.yml"
    a = main.render_topology(src, "aaaaaa1111", 0)
    b = main.render_topology(src, "bbbbbb2222", 1)
    assert a["name"] == "mtaaaaaa1111" and b["name"] == "mtbbbbbb2222"
    assert a["mgmt"]["ipv4-subnet"] == "172.31.0.0/24"
    assert b["mgmt"]["ipv4-subnet"] == "172.31.1.0/24"
    assert a["mgmt"]["network"] != b["mgmt"]["network"]
    assert a["topology"]["defaults"]["memory"] == "512MB"
    assert set(a["topology"]["nodes"]) == {"r1", "r2", "r3"}


def test_all_lab_definitions_valid():
    for d in sorted(main.cfg.labs_dir.iterdir()):
        data = main.load_labdef(d.name)
        nodes = {n["name"] for n in data["nodes"]}
        topo = main.render_topology(d / "topology.clab.yml", "abcdef1234", 0)
        assert nodes == set(topo["topology"]["nodes"]), d.name
        for chk in data["checks"]:
            assert chk["node"] in nodes


def test_requires_token(client):
    assert client.get("/health").status_code == 401
    assert client.get("/health", headers={"Authorization": "Bearer wrong"}).status_code == 401


def test_lifecycle(client):
    r = client.post("/labs", json={"id": "abcdef1234", "topology": "linux-basics", "ttl_minutes": 30}, headers=AUTH)
    assert r.status_code == 202, r.text
    # fon vazifasi (deploy) tugashini kutamiz
    for _ in range(50):
        if client.get("/labs/abcdef1234", headers=AUTH).json()["status"] != "provisioning":
            break
        asyncio.run(asyncio.sleep(0.02))
    assert client.get("/labs/abcdef1234", headers=AUTH).json()["status"] == "running"
    assert any(c[:2] == ("containerlab", "deploy") for c in client.calls)
    term = next(c for c in client.calls if c[:2] == ("docker", "run"))
    assert "lab-shell" in term and "mtabcdef1234" in term and "host1:bash" in term

    res = client.post("/labs/abcdef1234/check", headers=AUTH).json()["results"]
    by_id = {r["id"]: r["ok"] for r in res}
    assert by_id["h1-ip"] is True and by_id["ping"] is False

    assert client.post("/labs", json={"id": "abcdef1234", "topology": "linux-basics"}, headers=AUTH).status_code == 409
    assert client.post("/labs", json={"id": "BAD;rm", "topology": "linux-basics"}, headers=AUTH).status_code == 422
    assert client.post("/labs", json={"id": "zzzzzz9999", "topology": "../etc"}, headers=AUTH).status_code == 422

    assert client.delete("/labs/abcdef1234", headers=AUTH).status_code == 200
    assert client.get("/labs/abcdef1234", headers=AUTH).status_code == 404
    assert any(c[:2] == ("containerlab", "destroy") for c in client.calls)
