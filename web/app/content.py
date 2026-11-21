"""Kontent katalogi: courses/*/course.yaml, labs/*/lab.yaml va markdown darslar.

Kurs tuzilmasi (course.yaml):

    slug: routing
    title: Marshrutlash
    icon: "🧭"
    level: O'rta
    order: 3
    modules:
      - title: Dinamik marshrutlash
        lessons:
          - slug: ospf
            title: OSPF asoslari
            file: lessons/01-ospf.md     # kurs papkasiga nisbatan
            duration: 45
            lab: ospf-triangle           # labs/<nom>
            quiz: [...]                  # ixtiyoriy (front-matter da ham bo'lishi mumkin)

Dars faylida YAML front-matter bo'lishi mumkin (title, duration, lab, quiz).
Fayli mavjud bo'lmagan dars "tez orada" holatida ko'rsatiladi.
"""
from __future__ import annotations

import html
import logging
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from markdown_it import MarkdownIt
from mdit_py_plugins.anchors import anchors_plugin

log = logging.getLogger(__name__)

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
FRONT_MATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


@dataclass
class Question:
    text: str
    options: list[str]
    answer: int
    explain: str = ""


@dataclass
class Lesson:
    slug: str
    title: str
    course_slug: str
    module_title: str
    path: Path | None
    duration: int = 30
    lab: str | None = None
    kind: str = "lecture"  # lecture | lab | project
    quiz: list[Question] = field(default_factory=list)

    @property
    def available(self) -> bool:
        return self.path is not None and self.path.is_file()

    @property
    def url(self) -> str:
        return f"/courses/{self.course_slug}/{self.slug}"


@dataclass
class Module:
    title: str
    lessons: list[Lesson]


@dataclass
class Course:
    slug: str
    title: str
    description: str
    icon: str
    level: str
    order: int
    tags: list[str]
    color: str
    modules: list[Module]
    status: str = "active"  # active | soon

    @property
    def lessons(self) -> list[Lesson]:
        return [lsn for m in self.modules for lsn in m.lessons]

    @property
    def available_lessons(self) -> list[Lesson]:
        return [lsn for lsn in self.lessons if lsn.available]

    @property
    def total_minutes(self) -> int:
        return sum(lsn.duration for lsn in self.lessons)

    def get_lesson(self, slug: str) -> Lesson | None:
        return next((lsn for lsn in self.lessons if lsn.slug == slug), None)

    def neighbors(self, slug: str) -> tuple[Lesson | None, Lesson | None]:
        items = self.lessons
        for i, lsn in enumerate(items):
            if lsn.slug == slug:
                return (items[i - 1] if i > 0 else None, items[i + 1] if i + 1 < len(items) else None)
        return None, None


@dataclass
class LabCheck:
    id: str
    title: str
    node: str
    cmd: str
    expect: str


@dataclass
class LabNode:
    name: str
    shell: str = "bash"


@dataclass
class LabDef:
    slug: str
    title: str
    description: str
    duration: int
    level: str
    nodes: list[LabNode]
    checks: list[LabCheck]
    dir: Path
    tags: list[str] = field(default_factory=list)

    @property
    def readme(self) -> Path:
        return self.dir / "README.md"


def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    m = FRONT_MATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        log.warning("Front-matter xatosi: %s", exc)
        meta = {}
    return (meta if isinstance(meta, dict) else {}), text[m.end():]


def _parse_quiz(raw: Any, where: str) -> list[Question]:
    out: list[Question] = []
    for i, q in enumerate(raw or []):
        try:
            options = [str(o) for o in q["options"]]
            answer = int(q["answer"])
            if not 0 <= answer < len(options):
                raise ValueError("answer indeksi options chegarasidan tashqarida")
            out.append(Question(str(q["q"]), options, answer, str(q.get("explain", ""))))
        except (KeyError, TypeError, ValueError) as exc:
            log.warning("%s: %d-savol noto'g'ri (%s)", where, i + 1, exc)
    return out


class Catalog:
    def __init__(self, content_dir: Path) -> None:
        self.content_dir = content_dir.resolve()
        self.courses: dict[str, Course] = {}
        self.labs: dict[str, LabDef] = {}
        self.errors: list[str] = []
        self.reload()

    # ------------------------------------------------------------------ load
    def reload(self) -> None:
        self.errors = []
        self.labs = self._load_labs()
        courses: dict[str, Course] = {}
        for cfile in sorted((self.content_dir / "courses").glob("*/course.yaml")):
            try:
                course = self._load_course(cfile)
            except Exception as exc:  # noqa: BLE001 — bitta buzuq kurs butun saytni yiqitmasin
                self.errors.append(f"{cfile}: {exc}")
                log.exception("Kursni yuklab bo'lmadi: %s", cfile)
                continue
            courses[course.slug] = course
        self.courses = dict(sorted(courses.items(), key=lambda kv: (kv[1].order, kv[1].title)))
        render_markdown_file.cache_clear()

    def _inside(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self.content_dir)
            return True
        except ValueError:
            return False

    def _load_course(self, cfile: Path) -> Course:
        data = yaml.safe_load(cfile.read_text(encoding="utf-8")) or {}
        slug = str(data.get("slug") or cfile.parent.name)
        if not SLUG_RE.match(slug):
            raise ValueError(f"noto'g'ri slug: {slug!r}")
        modules: list[Module] = []
        seen: set[str] = set()
        for mod in data.get("modules") or []:
            lessons: list[Lesson] = []
            for item in mod.get("lessons") or []:
                lslug = str(item["slug"])
                if not SLUG_RE.match(lslug) or lslug in seen:
                    raise ValueError(f"dars slug noto'g'ri yoki takror: {lslug!r}")
                seen.add(lslug)
                path: Path | None = None
                meta: dict[str, Any] = {}
                if item.get("file"):
                    candidate = (cfile.parent / str(item["file"])).resolve()
                    if not self._inside(candidate):
                        raise ValueError(f"fayl kontent papkasidan tashqarida: {item['file']}")
                    path = candidate
                    if candidate.is_file():
                        meta, _ = split_front_matter(candidate.read_text(encoding="utf-8"))
                merged = {**meta, **item}
                lab = merged.get("lab")
                if lab and lab not in self.labs:
                    self.errors.append(f"{slug}/{lslug}: lab topilmadi: {lab}")
                lessons.append(
                    Lesson(
                        slug=lslug,
                        title=str(merged.get("title") or lslug),
                        course_slug=slug,
                        module_title=str(mod.get("title", "")),
                        path=path,
                        duration=int(merged.get("duration", 30)),
                        lab=str(lab) if lab else None,
                        kind=str(merged.get("kind", "lab" if lab else "lecture")),
                        quiz=_parse_quiz(merged.get("quiz"), f"{slug}/{lslug}"),
                    )
                )
            modules.append(Module(title=str(mod.get("title", "")), lessons=lessons))
        return Course(
            slug=slug,
            title=str(data.get("title", slug)),
            description=str(data.get("description", "")).strip(),
            icon=str(data.get("icon", "📘")),
            level=str(data.get("level", "")),
            order=int(data.get("order", 100)),
            tags=[str(t) for t in data.get("tags") or []],
            color=str(data.get("color", "#3b82f6")),
            modules=modules,
            status=str(data.get("status", "active")),
        )

    def _load_labs(self) -> dict[str, LabDef]:
        labs: dict[str, LabDef] = {}
        for lfile in sorted((self.content_dir / "labs").glob("*/lab.yaml")):
            try:
                data = yaml.safe_load(lfile.read_text(encoding="utf-8")) or {}
                slug = lfile.parent.name
                if not SLUG_RE.match(slug):
                    raise ValueError(f"noto'g'ri lab nomi: {slug!r}")
                labs[slug] = LabDef(
                    slug=slug,
                    title=str(data.get("title", slug)),
                    description=str(data.get("description", "")).strip(),
                    duration=int(data.get("duration", 60)),
                    level=str(data.get("level", "")),
                    nodes=[LabNode(str(n["name"]), str(n.get("shell", "bash"))) for n in data.get("nodes", [])],
                    checks=[
                        LabCheck(str(c["id"]), str(c["title"]), str(c["node"]), str(c["cmd"]), str(c["expect"]))
                        for c in data.get("checks", [])
                    ],
                    dir=lfile.parent,
                    tags=[str(t) for t in data.get("tags") or []],
                )
            except Exception as exc:  # noqa: BLE001
                self.errors.append(f"{lfile}: {exc}")
                log.exception("Labni yuklab bo'lmadi: %s", lfile)
        return labs

    # --------------------------------------------------------------- helpers
    def link_map(self) -> dict[str, str]:
        """Markdown ichidagi nisbiy .md havolalarni platforma URL ga aylantirish uchun."""
        return {str(lsn.path): lsn.url for c in self.courses.values() for lsn in c.lessons if lsn.path}

    def render_lesson(self, lesson: Lesson) -> tuple[str, list[tuple[str, str]]]:
        if not lesson.available or lesson.path is None:
            return "", []
        return render_markdown_file(str(lesson.path), lesson.path.stat().st_mtime_ns, _FrozenMap(self.link_map()))

    def render_lab_readme(self, lab: LabDef) -> str:
        if not lab.readme.is_file():
            return f"<p>{html.escape(lab.description)}</p>"
        return render_markdown_file(str(lab.readme), lab.readme.stat().st_mtime_ns, _FrozenMap({}))[0]


class _FrozenMap(dict):
    """lru_cache uchun hash qilinadigan dict (kontent qayta yuklanganda kesh tozalanadi)."""

    def __hash__(self) -> int:  # type: ignore[override]
        return hash(tuple(sorted(self.items())))


# ----------------------------------------------------------------- markdown
def _build_md() -> MarkdownIt:
    md = MarkdownIt("commonmark", {"html": True, "typographer": False})
    md.enable(["table", "strikethrough"])
    md.use(anchors_plugin, min_level=1, max_level=4, permalink=False)

    default_fence = md.renderer.rules["fence"]

    def fence(self, tokens, idx, options, env):  # noqa: ANN001
        token = tokens[idx]
        if token.info.strip().lower() == "mermaid":
            return f'<pre class="mermaid">{html.escape(token.content)}</pre>\n'
        return default_fence(tokens, idx, options, env)

    def table_open(self, tokens, idx, options, env):  # noqa: ANN001
        return '<div class="table-wrap"><table>\n'

    def table_close(self, tokens, idx, options, env):  # noqa: ANN001
        return "</table></div>\n"

    md.add_render_rule("fence", fence)
    md.add_render_rule("table_open", table_open)
    md.add_render_rule("table_close", table_close)
    return md


_MD = _build_md()
_MD_LINK = re.compile(r"^(?![a-z][a-z0-9+.-]*:|/|#)([^#?]+\.md)(#.*)?$", re.I)


@lru_cache(maxsize=512)
def render_markdown_file(path: str, _mtime: int, link_map: _FrozenMap) -> tuple[str, list[tuple[str, str]]]:
    text = Path(path).read_text(encoding="utf-8")
    _, body = split_front_matter(text)
    tokens = _MD.parse(body, {})
    base = Path(path).parent
    toc: list[tuple[str, str]] = []
    for i, tok in enumerate(tokens):
        if tok.type == "heading_open" and tok.tag == "h2":
            inline = tokens[i + 1]
            toc.append((str(tok.attrs.get("id", "")), inline.content))
        if tok.type == "inline" and tok.children:
            for child in tok.children:
                if child.type == "link_open":
                    href = str(child.attrs.get("href", ""))
                    m = _MD_LINK.match(href)
                    if m:
                        target = str((base / m.group(1)).resolve())
                        if target in link_map:
                            child.attrs["href"] = link_map[target] + (m.group(2) or "")
    return _MD.renderer.render(tokens, _MD.options, {}), toc


_catalog: Catalog | None = None


def get_catalog() -> Catalog:
    global _catalog
    if _catalog is None:
        from .config import settings

        _catalog = Catalog(settings.content_dir)
    return _catalog
