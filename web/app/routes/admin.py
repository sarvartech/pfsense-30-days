from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import labs_client
from ..config import settings
from ..content import get_catalog
from ..db import get_db
from ..models import LabSession, Progress, QuizAttempt, User
from ..web import flash, redirect, render, require_admin

router = APIRouter(prefix="/admin")


@router.get("")
async def admin_home(request: Request, user: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.execute(
        select(User, func.count(Progress.id))
        .outerjoin(Progress, Progress.user_id == User.id)
        .group_by(User.id)
        .order_by(User.created_at.desc())
        .limit(200)
    ).all()
    labs = db.scalars(select(LabSession).order_by(LabSession.created_at.desc()).limit(50)).all()
    agent = None
    agent_error = None
    if settings.labs_enabled:
        try:
            agent = await labs_client.agent_health()
        except labs_client.LabAgentError as exc:
            agent_error = str(exc)
    stats = {
        "users": db.scalar(select(func.count(User.id))),
        "completions": db.scalar(select(func.count(Progress.id))),
        "quizzes": db.scalar(select(func.count(QuizAttempt.id))),
        "labs": db.scalar(select(func.count(LabSession.id))),
    }
    return render(
        request,
        "admin/index.html",
        user=user,
        users=users,
        labs=labs,
        stats=stats,
        agent=agent,
        agent_error=agent_error,
        content_errors=get_catalog().errors,
    )


@router.post("/reload")
def reload_content(request: Request, user: User = Depends(require_admin)):
    catalog = get_catalog()
    catalog.reload()
    flash(
        request,
        f"Kontent qayta yuklandi: {len(catalog.courses)} kurs, {len(catalog.labs)} lab, {len(catalog.errors)} xato.",
        "success" if not catalog.errors else "error",
    )
    return redirect("/admin")
