from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..content import Course, get_catalog
from ..db import get_db
from ..models import LabSession, Progress, QuizAttempt, User
from ..web import current_user, flash, redirect, render, require_user

router = APIRouter()


def completed_set(db: Session, user: User | None, course_slug: str | None = None) -> set[tuple[str, str]]:
    if not user:
        return set()
    q = select(Progress.course_slug, Progress.lesson_slug).where(Progress.user_id == user.id)
    if course_slug:
        q = q.where(Progress.course_slug == course_slug)
    return {(c, s) for c, s in db.execute(q).all()}


def course_percent(course: Course, done: set[tuple[str, str]]) -> int:
    total = len(course.available_lessons)
    if not total:
        return 0
    n = sum(1 for lsn in course.available_lessons if (course.slug, lsn.slug) in done)
    return round(100 * n / total)


def _get_course(slug: str) -> Course:
    course = get_catalog().courses.get(slug)
    if not course:
        raise HTTPException(404, "Kurs topilmadi")
    return course


@router.get("/")
def index(request: Request, user: User | None = Depends(current_user), db: Session = Depends(get_db)):
    catalog = get_catalog()
    done = completed_set(db, user)
    stats = {
        "courses": len(catalog.courses),
        "lessons": sum(len(c.available_lessons) for c in catalog.courses.values()),
        "labs": len(catalog.labs),
    }
    percents = {c.slug: course_percent(c, done) for c in catalog.courses.values()}
    return render(request, "index.html", user=user, stats=stats, percents=percents)


@router.get("/courses")
def courses_list(request: Request):
    return redirect("/#courses")


@router.get("/courses/{slug}")
def course_page(slug: str, request: Request, user: User | None = Depends(current_user), db: Session = Depends(get_db)):
    course = _get_course(slug)
    done = completed_set(db, user, slug)
    first = next(iter(course.available_lessons), None)
    resume = next((lsn for lsn in course.available_lessons if (slug, lsn.slug) not in done), first)
    return render(
        request,
        "courses/course.html",
        user=user,
        course=course,
        done=done,
        percent=course_percent(course, done),
        resume=resume,
    )


@router.get("/courses/{slug}/{lesson_slug}")
def lesson_page(
    slug: str,
    lesson_slug: str,
    request: Request,
    user: User | None = Depends(current_user),
    db: Session = Depends(get_db),
):
    catalog = get_catalog()
    course = _get_course(slug)
    lesson = course.get_lesson(lesson_slug)
    if not lesson:
        raise HTTPException(404, "Dars topilmadi")
    body, toc = catalog.render_lesson(lesson)
    prev, nxt = course.neighbors(lesson_slug)
    done = completed_set(db, user, slug)
    last_attempt = None
    active_lab = None
    if user:
        last_attempt = db.scalar(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user.id, QuizAttempt.course_slug == slug, QuizAttempt.lesson_slug == lesson_slug)
            .order_by(QuizAttempt.id.desc())
        )
        labs = db.scalars(
            select(LabSession).where(LabSession.user_id == user.id, LabSession.status.in_(LabSession.ACTIVE))
        ).all()
        active_lab = next((lab for lab in labs if lab.is_active), None)
    return render(
        request,
        "courses/lesson.html",
        user=user,
        course=course,
        lesson=lesson,
        body=body,
        toc=toc,
        prev=prev,
        nxt=nxt,
        done=done,
        is_done=(slug, lesson_slug) in done,
        lab=catalog.labs.get(lesson.lab) if lesson.lab else None,
        active_lab=active_lab,
        last_attempt=last_attempt,
        quiz_result=None,
    )


@router.post("/courses/{slug}/{lesson_slug}/complete")
def toggle_complete(
    slug: str, lesson_slug: str, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)
):
    course = _get_course(slug)
    if not course.get_lesson(lesson_slug):
        raise HTTPException(404)
    row = db.scalar(
        select(Progress).where(
            Progress.user_id == user.id, Progress.course_slug == slug, Progress.lesson_slug == lesson_slug
        )
    )
    if row:
        db.delete(row)
        flash(request, "Dars belgisi olib tashlandi.")
        target = f"/courses/{slug}/{lesson_slug}"
    else:
        db.add(Progress(user_id=user.id, course_slug=slug, lesson_slug=lesson_slug))
        flash(request, "Dars tugallandi ✅", "success")
        _, nxt = course.neighbors(lesson_slug)
        target = nxt.url if nxt and nxt.available else f"/courses/{slug}"
    db.commit()
    return redirect(target)


@router.post("/courses/{slug}/{lesson_slug}/quiz")
async def submit_quiz(
    slug: str, lesson_slug: str, request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)
):
    catalog = get_catalog()
    course = _get_course(slug)
    lesson = course.get_lesson(lesson_slug)
    if not lesson or not lesson.quiz:
        raise HTTPException(404)
    form = await request.form()
    answers: list[int | None] = []
    for i in range(len(lesson.quiz)):
        raw = form.get(f"q{i}")
        try:
            answers.append(int(str(raw)) if raw is not None else None)
        except ValueError:
            answers.append(None)
    score = sum(1 for q, a in zip(lesson.quiz, answers) if a == q.answer)
    attempt = QuizAttempt(user_id=user.id, course_slug=slug, lesson_slug=lesson_slug, score=score, total=len(lesson.quiz))
    db.add(attempt)
    passed = score * 100 >= 70 * len(lesson.quiz)
    if passed:
        exists = db.scalar(
            select(Progress).where(
                Progress.user_id == user.id, Progress.course_slug == slug, Progress.lesson_slug == lesson_slug
            )
        )
        if not exists:
            db.add(Progress(user_id=user.id, course_slug=slug, lesson_slug=lesson_slug))
    db.commit()

    body, toc = catalog.render_lesson(lesson)
    prev, nxt = course.neighbors(lesson_slug)
    done = completed_set(db, user, slug)
    return render(
        request,
        "courses/lesson.html",
        user=user,
        course=course,
        lesson=lesson,
        body=body,
        toc=toc,
        prev=prev,
        nxt=nxt,
        done=done,
        is_done=(slug, lesson_slug) in done,
        lab=catalog.labs.get(lesson.lab) if lesson.lab else None,
        active_lab=None,
        last_attempt=attempt,
        quiz_result={"answers": answers, "score": score, "total": len(lesson.quiz), "passed": passed},
    )


@router.get("/dashboard")
def dashboard(request: Request, user: User = Depends(require_user), db: Session = Depends(get_db)):
    catalog = get_catalog()
    done = completed_set(db, user)
    started = [
        (c, course_percent(c, done))
        for c in catalog.courses.values()
        if any(cs == c.slug for cs, _ in done)
    ]
    attempts = db.scalars(
        select(QuizAttempt).where(QuizAttempt.user_id == user.id).order_by(QuizAttempt.id.desc()).limit(10)
    ).all()
    labs = db.scalars(
        select(LabSession).where(LabSession.user_id == user.id).order_by(LabSession.created_at.desc()).limit(10)
    ).all()
    return render(
        request,
        "dashboard.html",
        user=user,
        started=started,
        attempts=attempts,
        labs=labs,
        total_done=len(done),
    )
