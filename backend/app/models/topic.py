from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.catalog import Skill


class Topic(Base, TimestampMixin):
    """Topic/category for organizing skills (e.g., Arithmetic, Algebra, Geometry)."""
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    icon: Mapped[str | None] = mapped_column(String(64), nullable=True)  # emoji or icon name
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # for sorting
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    skills: Mapped[list["Skill"]] = relationship(back_populates="topic")

