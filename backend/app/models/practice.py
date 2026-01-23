from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint

from app.db.base import Base
from app.models.enums import MistakeType, PracticeZone
from app.models.mixins import TimestampMixin


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True, nullable=False)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Backwards compatible counters
    questions_answered: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wrong_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    smartscore: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    time_elapsed_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # IXL-like variables
    current_smartscore: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    best_smartscore: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_questions_answered: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_incorrect: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_streak_correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_streak_correct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_zone: Mapped[PracticeZone] = mapped_column(
        Enum(PracticeZone, name="practice_zone"),
        nullable=False,
        default=PracticeZone.LEARNING,
        index=True,
    )
    last_question_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    active_time_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    inactivity_threshold_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=240)
    state: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False, default=dict)

    attempts: Mapped[list["PracticeAttempt"]] = relationship(back_populates="session")


class PracticeAttempt(Base):
    __tablename__ = "practice_attempts"
    # Убираем UniqueConstraint для question_id, так как для генераторов он может быть None
    # Можно добавить частичный индекс для уникальности только когда question_id не NULL
    # __table_args__ = (UniqueConstraint("session_id", "question_id", name="uq_attempt_session_question"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("practice_sessions.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id: Mapped[int | None] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=True)
    question_level: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    question_payload: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False, default=dict)
    submitted_answer: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False, default=dict)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mistake_type: Mapped[MistakeType | None] = mapped_column(Enum(MistakeType, name="mistake_type"), nullable=True)
    hints_used_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    explanation_viewed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    answered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    time_spent_sec: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    smartscore_before: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    smartscore_after: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    zone_before: Mapped[PracticeZone] = mapped_column(Enum(PracticeZone, name="practice_zone"), nullable=False, default=PracticeZone.LEARNING)
    zone_after: Mapped[PracticeZone] = mapped_column(Enum(PracticeZone, name="practice_zone"), nullable=False, default=PracticeZone.LEARNING)

    session: Mapped[PracticeSession] = relationship(back_populates="attempts")


class ProgressSnapshot(Base, TimestampMixin):
    __tablename__ = "progress_snapshots"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)

    # Backwards compatible
    best_smartscore: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_smartscore: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_practiced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accuracy_percent: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    best_smartscore_all_time: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_questions_answered_all_time: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_time_seconds_all_time: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
