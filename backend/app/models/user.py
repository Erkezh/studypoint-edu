from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.profile import StudentProfile
    from app.models.subscription import Subscription

from datetime import date

from sqlalchemy import Boolean, Enum, ForeignKey, String, Integer, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import UserRole
from app.models.mixins import TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), index=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Gamification Fields
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    coins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_study_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    parent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    teacher_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    profile: Mapped["StudentProfile"] = relationship(back_populates="user", uselist=False)
    subscription: Mapped["Subscription"] = relationship(back_populates="user", uselist=False)

    parent: Mapped["User"] = relationship(remote_side=[id], back_populates="children", foreign_keys=[parent_id])
    children: Mapped[list["User"]] = relationship(back_populates="parent", cascade="all, delete-orphan", foreign_keys=[parent_id])

    teacher: Mapped["User"] = relationship(remote_side=[id], back_populates="students", foreign_keys=[teacher_id])
    students: Mapped[list["User"]] = relationship(back_populates="teacher", cascade="all, delete-orphan", foreign_keys=[teacher_id])

