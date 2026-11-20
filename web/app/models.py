from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Progress(Base):
    __tablename__ = "progress"
    __table_args__ = (UniqueConstraint("user_id", "course_slug", "lesson_slug"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_slug: Mapped[str] = mapped_column(String(80))
    lesson_slug: Mapped[str] = mapped_column(String(120))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    course_slug: Mapped[str] = mapped_column(String(80))
    lesson_slug: Mapped[str] = mapped_column(String(120))
    score: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class LabSession(Base):
    __tablename__ = "lab_sessions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    topology: Mapped[str] = mapped_column(String(80))
    course_slug: Mapped[str | None] = mapped_column(String(80), nullable=True)
    lesson_slug: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # provisioning | running | error | stopped | expired
    status: Mapped[str] = mapped_column(String(20), default="provisioning")
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    checks_passed: Mapped[int] = mapped_column(Integer, default=0)
    checks_total: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    ACTIVE = ("provisioning", "running")

    @property
    def is_active(self) -> bool:
        exp = self.expires_at
        if exp.tzinfo is None:  # SQLite tz ma'lumotini saqlamaydi
            exp = exp.replace(tzinfo=timezone.utc)
        return self.status in self.ACTIVE and exp > utcnow()

    @property
    def expires_at_utc(self) -> datetime:
        exp = self.expires_at
        return exp if exp.tzinfo else exp.replace(tzinfo=timezone.utc)
