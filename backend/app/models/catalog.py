from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Subject(Base, TimestampMixin):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)

    skills: Mapped[list["Skill"]] = relationship(back_populates="subject")


class Grade(Base, TimestampMixin):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[int] = mapped_column(Integer, unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(64), nullable=False)

    skills: Mapped[list["Skill"]] = relationship(back_populates="grade")


class Skill(Base, TimestampMixin):
    __tablename__ = "skills"
    __table_args__ = (
        UniqueConstraint("subject_id", "grade_id", "code", name="uq_skill_code_grade_subject"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    grade_id: Mapped[int] = mapped_column(ForeignKey("grades.id", ondelete="CASCADE"), index=True, nullable=False)
    topic_id: Mapped[int | None] = mapped_column(ForeignKey("topics.id", ondelete="SET NULL"), index=True, nullable=True)

    code: Mapped[str] = mapped_column(String(16), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(64)), nullable=False, default=list)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    example_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Код генератора задач - выполняется для создания задач динамически
    generator_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Метаданные генератора (параметры, настройки)
    generator_metadata: Mapped[dict] = mapped_column(MutableDict.as_mutable(JSONB), nullable=False, default=dict)

    subject: Mapped[Subject] = relationship(back_populates="skills")
    grade: Mapped[Grade] = relationship(back_populates="skills")
    topic: Mapped["Topic"] = relationship(back_populates="skills")
    questions: Mapped[list["Question"]] = relationship(back_populates="skill")

