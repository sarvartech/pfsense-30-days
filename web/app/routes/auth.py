from __future__ import annotations

import re

from fastapi import APIRouter, Depends, Form, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import User
from ..security import hash_password, verify_password
from ..web import current_user, flash, redirect, render, safe_next

router = APIRouter()
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@router.get("/login")
def login_form(request: Request, next: str = "", user: User | None = Depends(current_user)):
    if user:
        return redirect(safe_next(next))
    return render(request, "auth/login.html", next=next)


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: str = Form(""),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(func.lower(User.email) == email.strip().lower()))
    if not user or not verify_password(password, user.password_hash):
        flash(request, "Email yoki parol noto'g'ri.", "error")
        return render(request, "auth/login.html", next=next, email=email, status_code=400)
    request.session.clear()
    request.session["uid"] = user.id
    flash(request, f"Xush kelibsiz, {user.name}!", "success")
    return redirect(safe_next(next))


@router.get("/register")
def register_form(request: Request, user: User | None = Depends(current_user)):
    if user:
        return redirect("/dashboard")
    return render(request, "auth/register.html")


@router.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    db: Session = Depends(get_db),
):
    if not settings.allow_registration:
        flash(request, "Ro'yxatdan o'tish vaqtincha yopiq.", "error")
        return redirect("/login")
    email_n = email.strip().lower()
    errors = []
    if not name.strip() or len(name) > 120:
        errors.append("Ism kiritilishi shart.")
    if not EMAIL_RE.match(email_n):
        errors.append("Email manzil noto'g'ri.")
    if len(password) < 8:
        errors.append("Parol kamida 8 ta belgidan iborat bo'lsin.")
    if password != password2:
        errors.append("Parollar mos kelmadi.")
    if not errors and db.scalar(select(User).where(func.lower(User.email) == email_n)):
        errors.append("Bu email allaqachon ro'yxatdan o'tgan.")
    if errors:
        for e in errors:
            flash(request, e, "error")
        return render(request, "auth/register.html", name=name, email=email, status_code=400)

    user = User(
        email=email_n,
        name=name.strip(),
        password_hash=hash_password(password),
        is_admin=email_n in settings.admin_emails,
    )
    db.add(user)
    db.commit()
    request.session.clear()
    request.session["uid"] = user.id
    flash(request, "Hisob yaratildi. O'qishni boshlang! 🚀", "success")
    return redirect("/dashboard")


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return redirect("/")
