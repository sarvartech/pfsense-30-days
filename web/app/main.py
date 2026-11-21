from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager, suppress
from pathlib import Path
from urllib.parse import quote, urlsplit

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from . import labs_client
from .config import settings
from .content import get_catalog
from .db import SessionLocal, init_db
from .models import LabSession, utcnow
from .routes import admin, auth, courses, labs
from .web import LoginRequired, current_user, redirect, render

logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)
log = logging.getLogger("men-tarmoq")


async def reap_expired_labs() -> None:
    """Muddati o'tgan laboratoriyalarni home serverdan o'chiradi."""
    while True:
        await asyncio.sleep(60)
        try:
            with SessionLocal() as db:
                now = utcnow()
                for lab in db.scalars(select(LabSession).where(LabSession.status.in_(LabSession.ACTIVE))):
                    if lab.expires_at_utc <= now:
                        with suppress(labs_client.LabAgentError):
                            await labs_client.destroy_lab(lab.id)
                        lab.status = "expired"
                db.commit()
        except Exception:  # noqa: BLE001
            log.exception("Lab reaper xatosi")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    catalog = get_catalog()
    log.info("Kontent: %d kurs, %d lab (%s)", len(catalog.courses), len(catalog.labs), settings.content_dir)
    for err in catalog.errors:
        log.warning("Kontent xatosi: %s", err)
    task = asyncio.create_task(reap_expired_labs()) if settings.labs_enabled else None
    yield
    if task:
        task.cancel()


app = FastAPI(title=settings.site_name, lifespan=lifespan, docs_url=None, redoc_url=None)


@app.middleware("http")
async def origin_check(request: Request, call_next):
    """Oddiy CSRF himoyasi: POST so'rovlar faqat o'z domenimizdan kelishi kerak."""
    if request.method == "POST":
        origin = request.headers.get("origin")
        if origin and origin != "null":
            host = request.headers.get("x-forwarded-host") or request.headers.get("host", "")
            if urlsplit(origin).netloc != host:
                return PlainTextResponse("Origin mos emas", status_code=403)
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("Referrer-Policy", "same-origin")
    return response


app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    session_cookie="mt_session",
    max_age=60 * 60 * 24 * 14,
    same_site="lax",
    https_only=settings.https_only,
)
app.mount("/static", StaticFiles(directory=str(Path(__file__).parent / "static")), name="static")
app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(labs.router)
app.include_router(admin.router)


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.exception_handler(LoginRequired)
async def login_required_handler(request: Request, exc: LoginRequired):
    return redirect(f"/login?next={quote(exc.next_url)}")


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    if request.url.path.startswith(("/internal/", "/static/")) or request.url.path.endswith(".json"):
        return PlainTextResponse(str(exc.detail), status_code=exc.status_code)
    with SessionLocal() as db:
        user = current_user(request, db)
        return render(request, "error.html", user=user, code=exc.status_code, detail=exc.detail, status_code=exc.status_code)
