from __future__ import annotations

import logging
import re
import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import labs_client
from ..config import settings
from ..content import get_catalog
from ..db import get_db
from ..models import LabSession, User, utcnow
from ..web import current_user, flash, redirect, render, require_user

log = logging.getLogger(__name__)
router = APIRouter()
TERM_URI_RE = re.compile(r"^" + re.escape(settings.term_base_path) + r"/([a-z0-9]{6,32})(?:/|$)")


def _own_lab(db: Session, lab_id: str, user: User) -> LabSession:
    lab = db.get(LabSession, lab_id)
    if not lab or (lab.user_id != user.id and not user.is_admin):
        raise HTTPException(404, "Laboratoriya topilmadi")
    return lab


@router.get("/labs")
def labs_catalog(request: Request, user: User | None = Depends(current_user), db: Session = Depends(get_db)):
    active = []
    if user:
        active = [
            lab
            for lab in db.scalars(
                select(LabSession).where(LabSession.user_id == user.id, LabSession.status.in_(LabSession.ACTIVE))
            )
            if lab.is_active
        ]
    return render(request, "labs/catalog.html", user=user, active=active)


@router.post("/labs/start")
async def start_lab(
    request: Request,
    topology: str = Form(...),
    course: str = Form(""),
    lesson: str = Form(""),
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    catalog = get_catalog()
    if topology not in catalog.labs:
        raise HTTPException(404, "Bunday laboratoriya yo'q")
    if not settings.labs_enabled:
        flash(request, "Jonli laboratoriyalar hozircha o'chirilgan (lab server ulanmagan).", "error")
        return redirect(request.headers.get("referer") or "/labs")

    active = [
        lab
        for lab in db.scalars(
            select(LabSession).where(LabSession.user_id == user.id, LabSession.status.in_(LabSession.ACTIVE))
        )
        if lab.is_active
    ]
    if len(active) >= settings.max_labs_per_user and not user.is_admin:
        flash(request, "Sizda allaqachon faol laboratoriya bor. Avval uni to'xtating.", "error")
        return redirect(f"/labs/{active[0].id}")

    lab_id = secrets.token_hex(5)
    try:
        await labs_client.create_lab(lab_id, topology, settings.lab_ttl_minutes)
    except labs_client.LabAgentError as exc:
        flash(request, str(exc), "error")
        return redirect(request.headers.get("referer") or "/labs")

    db.add(
        LabSession(
            id=lab_id,
            user_id=user.id,
            topology=topology,
            course_slug=course or None,
            lesson_slug=lesson or None,
            status="provisioning",
            checks_total=len(catalog.labs[topology].checks),
            expires_at=utcnow() + timedelta(minutes=settings.lab_ttl_minutes),
        )
    )
    db.commit()
    return redirect(f"/labs/{lab_id}")


@router.get("/labs/{lab_id}")
def lab_page(lab_id: str, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)):
    lab = _own_lab(db, lab_id, user)
    catalog = get_catalog()
    labdef = catalog.labs.get(lab.topology)
    return render(
        request,
        "labs/session.html",
        user=user,
        lab=lab,
        labdef=labdef,
        readme=catalog.render_lab_readme(labdef) if labdef else "",
        term_url=f"{settings.term_base_path}/{lab.id}/",
    )


@router.get("/labs/{lab_id}/status.json")
async def lab_status(lab_id: str, user: User = Depends(require_user), db: Session = Depends(get_db)):
    lab = _own_lab(db, lab_id, user)
    if lab.status in LabSession.ACTIVE and not lab.is_active:
        lab.status = "expired"
        db.commit()
    if lab.status == "provisioning":
        try:
            info = await labs_client.lab_status(lab_id)
        except labs_client.LabAgentError as exc:
            return JSONResponse({"status": lab.status, "message": str(exc)})
        if info is None:
            lab.status, lab.message = "error", "Lab serverda topilmadi"
        else:
            lab.status = info.get("status", lab.status)
            lab.message = (info.get("message") or "")[:500] or None
        db.commit()
    return {
        "status": lab.status,
        "message": lab.message,
        "expires_at": lab.expires_at_utc.isoformat(),
        "checks_passed": lab.checks_passed,
        "checks_total": lab.checks_total,
    }


@router.post("/labs/{lab_id}/check")
async def lab_check(lab_id: str, user: User = Depends(require_user), db: Session = Depends(get_db)):
    lab = _own_lab(db, lab_id, user)
    if not lab.is_active:
        raise HTTPException(409, "Laboratoriya faol emas")
    try:
        result = await labs_client.run_checks(lab_id)
    except labs_client.LabAgentError as exc:
        return JSONResponse({"error": str(exc)}, status_code=502)
    results = result.get("results", [])
    lab.checks_passed = sum(1 for r in results if r.get("ok"))
    lab.checks_total = len(results)
    db.commit()
    return {"results": results, "passed": lab.checks_passed, "total": lab.checks_total}


@router.post("/labs/{lab_id}/stop")
async def stop_lab(lab_id: str, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)):
    lab = _own_lab(db, lab_id, user)
    try:
        await labs_client.destroy_lab(lab_id)
    except labs_client.LabAgentError as exc:
        log.warning("Lab %s ni o'chirishda xato: %s", lab_id, exc)
    lab.status = "stopped"
    db.commit()
    flash(request, "Laboratoriya to'xtatildi va resurslar bo'shatildi.", "success")
    if lab.course_slug and lab.lesson_slug:
        return redirect(f"/courses/{lab.course_slug}/{lab.lesson_slug}")
    return redirect("/labs")


@router.get("/internal/term-auth")
def term_auth(request: Request, user: User | None = Depends(current_user), db: Session = Depends(get_db)):
    """Caddy `forward_auth` shu endpointni chaqiradi: terminalga faqat lab egasi kira oladi."""
    uri = request.headers.get("x-forwarded-uri", "")
    m = TERM_URI_RE.match(uri)
    if not user or not m:
        return Response(status_code=401)
    lab = db.get(LabSession, m.group(1))
    if not lab or not lab.is_active or (lab.user_id != user.id and not user.is_admin):
        return Response(status_code=403)
    return Response(status_code=200)
