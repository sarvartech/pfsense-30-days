"""Shablonlar, joriy foydalanuvchi va flash xabarlar uchun umumiy yordamchilar."""
from __future__ import annotations

from typing import Any

from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .config import settings
from .content import get_catalog
from .db import get_db
from .models import User

templates = Jinja2Templates(directory=str(__import__("pathlib").Path(__file__).parent / "templates"))
templates.env.globals.update(settings=settings)


def flash(request: Request, message: str, kind: str = "info") -> None:
    request.session.setdefault("_flash", []).append({"m": message, "k": kind})


def pop_flashes(request: Request) -> list[dict[str, str]]:
    return request.session.pop("_flash", [])


def current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    uid = request.session.get("uid")
    if not uid:
        return None
    user = db.get(User, uid)
    if user is None:
        request.session.pop("uid", None)
    return user


class LoginRequired(Exception):
    def __init__(self, next_url: str) -> None:
        self.next_url = next_url


def require_user(request: Request, user: User | None = Depends(current_user)) -> User:
    if user is None:
        raise LoginRequired(request.url.path)
    return user


def require_admin(user: User = Depends(require_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Faqat administratorlar uchun")
    return user


def render(request: Request, template: str, user: User | None = None, status_code: int = 200, **ctx: Any):
    return templates.TemplateResponse(
        request,
        template,
        {"user": user, "flashes": pop_flashes(request), "catalog": get_catalog(), **ctx},
        status_code=status_code,
    )


def redirect(url: str) -> RedirectResponse:
    return RedirectResponse(url, status_code=303)


def safe_next(url: str | None) -> str:
    if url and url.startswith("/") and not url.startswith("//"):
        return url
    return "/dashboard"
