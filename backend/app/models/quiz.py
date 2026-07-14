from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import QuizQuestionOrder, QuizResultVisibility, QuizEndType
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.question import Question


class Quiz(Base, TimestampMixin):
    __tablename__ = "quizzes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    teacher_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    question_order: Mapped[QuizQuestionOrder] = mapped_column(
        Enum(QuizQuestionOrder, name="quiz_question_order"), 
        nullable=False, 
        default=QuizQuestionOrder.FIXED
    )
    result_visibility: Mapped[QuizResultVisibility] = mapped_column(
        Enum(QuizResultVisibility, name="quiz_result_visibility"), 
        nullable=False, 
        default=QuizResultVisibility.ALWAYS
    )
    ended_result_visibility: Mapped[QuizResultVisibility] = mapped_column(
        Enum(QuizResultVisibility, name="quiz_result_visibility"), 
        nullable=False, 
        default=QuizResultVisibility.ALWAYS
    )
    end_type: Mapped[QuizEndType] = mapped_column(
        Enum(QuizEndType, name="quiz_end_type"), 
        nullable=False, 
        default=QuizEndType.MANUAL
    )

    teacher: Mapped["User"] = relationship()
    questions: Mapped[list["QuizQuestion"]] = relationship(back_populates="quiz", cascade="all, delete-orphan", order_by="QuizQuestion.position")
    assignments: Mapped[list["QuizAssignment"]] = relationship(back_populates="quiz", cascade="all, delete-orphan")


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True, nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), index=True, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    seed: Mapped[int | None] = mapped_column(Integer, nullable=True)

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")
    question: Mapped["Question"] = relationship()


class QuizAssignment(Base, TimestampMixin):
    __tablename__ = "quiz_assignments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("quizzes.id", ondelete="CASCADE"), index=True, nullable=False)
    classroom_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("classrooms.id", ondelete="CASCADE"), index=True, nullable=True) # Optional if assigned to individuals
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True) # Optional if assigned to classroom
    
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_spent_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    question_results: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)

    quiz: Mapped["Quiz"] = relationship(back_populates="assignments")
