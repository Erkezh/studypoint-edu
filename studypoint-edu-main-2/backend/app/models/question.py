from __future__ import annotations

from sqlalchemy import Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import QuestionType
from app.models.mixins import TimestampMixin


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), index=True, nullable=False)
    type: Mapped[QuestionType] = mapped_column(Enum(QuestionType, name="question_type"), index=True, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    data: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False, default=dict)
    correct_answer: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False, default=dict)
    explanation: Mapped[str] = mapped_column(Text, nullable=False, default="")
    level: Mapped[int] = mapped_column(Integer, index=True, nullable=False, default=1)

    skill: Mapped["Skill"] = relationship(back_populates="questions")
