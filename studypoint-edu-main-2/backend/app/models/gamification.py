import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, Enum, ForeignKey, String, Integer, Date, DateTime, UniqueConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import GameType
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User

class ShopItem(Base):
    __tablename__ = "shop_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'hat', 'shirt', 'color'
    cost: Mapped[int] = mapped_column(Integer, nullable=False)
    rarity: Mapped[str] = mapped_column(String(50), nullable=False, default="common")
    asset_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    game_type: Mapped[GameType] = mapped_column(
        Enum(GameType, name="game_type", values_callable=lambda values: [value.value for value in values]),
        default=GameType.CHARACTER,
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String(80), default="accessories", nullable=False)
    required_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)


class UserItem(Base):
    __tablename__ = "user_items"
    __table_args__ = (UniqueConstraint("user_id", "item_id", name="uq_user_item_user_item"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shop_items.id", ondelete="CASCADE"), nullable=False)
    is_equipped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    criteria_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    reward_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reward_coins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    achievement_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class DailyMission(Base):
    __tablename__ = "daily_missions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    mission_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. 'solve_questions', 'win_pvp'
    target_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    reward_xp: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    reward_coins: Mapped[int] = mapped_column(Integer, default=10, nullable=False)


class UserMission(Base):
    __tablename__ = "user_missions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    mission_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("daily_missions.id", ondelete="CASCADE"), nullable=False)
    assigned_date: Mapped[date] = mapped_column(Date, nullable=False)
    current_progress: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class StudentGamification(Base, TimestampMixin):
    __tablename__ = "student_gamification"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    coins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    combo_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    daily_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_streak_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_problems_solved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class StudentWallet(Base, TimestampMixin):
    __tablename__ = "student_wallet"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    coins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    active_vehicle_id: Mapped[str | None] = mapped_column(String(80), ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True)
    total_problems_solved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class TopicReward(Base, TimestampMixin):
    __tablename__ = "topic_rewards"
    __table_args__ = (UniqueConstraint("student_id", "topic_id", name="uq_topic_reward_student_topic"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), index=True, nullable=False)
    rewarded_milestones: Mapped[list[int]] = mapped_column(JSON, default=list, nullable=False)


class StudentStreak(Base, TimestampMixin):
    __tablename__ = "student_streaks"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    streak_started_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    streak_sequence_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    last_7_day_reward_cycle: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    unlock_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    unlock_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    coin_price: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    level_required: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    xp_required: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    price: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    type: Mapped[str] = mapped_column(String(80), default="vehicle", nullable=False)
    model_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class StudentVehicle(Base):
    __tablename__ = "student_vehicles"
    __table_args__ = (UniqueConstraint("student_id", "vehicle_id", name="uq_student_vehicle"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    vehicle_id: Mapped[str] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), index=True, nullable=False)
    purchased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class OwnedVehicle(Base):
    __tablename__ = "owned_vehicles"
    __table_args__ = (UniqueConstraint("student_id", "vehicle_id", name="uq_owned_vehicle_student_vehicle"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    vehicle_id: Mapped[str] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), index=True, nullable=False)
    purchased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class LevelReward(Base):
    __tablename__ = "level_rewards"
    __table_args__ = (UniqueConstraint("student_id", "level", name="uq_level_reward_student_level"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    rewarded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class StreakReward(Base):
    __tablename__ = "streak_rewards"
    __table_args__ = (UniqueConstraint("student_id", "streak_sequence_id", "cycle_number", name="uq_streak_reward_sequence_cycle"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    streak_sequence_id: Mapped[str] = mapped_column(String(80), nullable=False)
    cycle_number: Mapped[int] = mapped_column(Integer, nullable=False)
    rewarded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class WalletTransaction(Base, TimestampMixin):
    __tablename__ = "wallet_transactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    transaction_type: Mapped[str] = mapped_column(String(80), nullable=False)
    xp_change: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    coin_change: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    xp_balance_after: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    coin_balance_after: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    transaction_metadata: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class RewardEvent(Base, TimestampMixin):
    __tablename__ = "reward_events"
    __table_args__ = (UniqueConstraint("idempotency_key", name="uq_reward_event_idempotency_key"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    idempotency_key: Mapped[str] = mapped_column(String(160), nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    reference_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    xp_awarded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    coins_awarded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    result: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)


class GarageItem(Base):
    __tablename__ = "garage_items"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    vehicle_type: Mapped[str] = mapped_column(String(80), default="all", nullable=False)
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    coin_price: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unlock_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    model_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rarity: Mapped[str] = mapped_column(String(50), default="common", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class StudentGarageItem(Base):
    __tablename__ = "student_garage_items"
    __table_args__ = (UniqueConstraint("student_id", "garage_item_id", name="uq_student_garage_item"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    garage_item_id: Mapped[str] = mapped_column(ForeignKey("garage_items.id", ondelete="CASCADE"), nullable=False)
    purchased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)


class SelectedVehicleCustomization(Base, TimestampMixin):
    __tablename__ = "selected_vehicle_customization"
    __table_args__ = (UniqueConstraint("student_id", "vehicle_id", name="uq_student_vehicle_customization"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    vehicle_id: Mapped[str] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), index=True, nullable=False)
    wheel_item_id: Mapped[str | None] = mapped_column(ForeignKey("garage_items.id", ondelete="SET NULL"), nullable=True)
    paint_item_id: Mapped[str | None] = mapped_column(ForeignKey("garage_items.id", ondelete="SET NULL"), nullable=True)
    roof_item_id: Mapped[str | None] = mapped_column(ForeignKey("garage_items.id", ondelete="SET NULL"), nullable=True)
    spoiler_item_id: Mapped[str | None] = mapped_column(ForeignKey("garage_items.id", ondelete="SET NULL"), nullable=True)
    headlight_item_id: Mapped[str | None] = mapped_column(ForeignKey("garage_items.id", ondelete="SET NULL"), nullable=True)
    sticker_item_id: Mapped[str | None] = mapped_column(ForeignKey("garage_items.id", ondelete="SET NULL"), nullable=True)
