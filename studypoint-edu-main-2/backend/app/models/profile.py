from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import GameType


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    grade_level: Mapped[int] = mapped_column(Integer, nullable=False)
    school: Mapped[str | None] = mapped_column(String(255), nullable=True)
    plain_password: Mapped[str | None] = mapped_column(String(128), nullable=True)
    active_game: Mapped[GameType | None] = mapped_column(
        Enum(GameType, name="game_type", values_callable=lambda values: [value.value for value in values]),
        nullable=True,
    )
    game_selected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_game_switch_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="profile")
