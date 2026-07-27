"""balanced gamification economy

Revision ID: 20260708_balanced_gamification
Revises: e4f6a1b2c3d4, 9d263add4300
Create Date: 2026-07-08 15:40:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260708_balanced_gamification"
down_revision = ("e4f6a1b2c3d4", "9d263add4300")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("vehicles", sa.Column("level_required", sa.Integer(), nullable=False, server_default="1"))
    op.add_column("vehicles", sa.Column("xp_required", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("vehicles", sa.Column("price", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("vehicles", sa.Column("type", sa.String(length=80), nullable=False, server_default="vehicle"))

    op.execute("UPDATE vehicles SET level_required = unlock_level, xp_required = unlock_xp, price = coin_price, type = slug")

    op.create_table(
        "student_wallet",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("coins", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("active_vehicle_id", sa.String(length=80), nullable=True),
        sa.Column("total_problems_solved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["active_vehicle_id"], ["vehicles.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("student_id"),
    )

    op.create_table(
        "topic_rewards",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("rewarded_milestones", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["topic_id"], ["skills.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", "topic_id", name="uq_topic_reward_student_topic"),
    )
    op.create_index("ix_topic_rewards_student_id", "topic_rewards", ["student_id"])
    op.create_index("ix_topic_rewards_topic_id", "topic_rewards", ["topic_id"])

    op.create_table(
        "student_streaks",
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_active_date", sa.Date(), nullable=True),
        sa.Column("last_7_day_reward_cycle", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("student_id"),
    )

    op.create_table(
        "owned_vehicles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vehicle_id", sa.String(length=80), nullable=False),
        sa.Column("purchased_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", "vehicle_id", name="uq_owned_vehicle_student_vehicle"),
    )
    op.create_index("ix_owned_vehicles_student_id", "owned_vehicles", ["student_id"])
    op.create_index("ix_owned_vehicles_vehicle_id", "owned_vehicles", ["vehicle_id"])

    op.create_table(
        "level_rewards",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("rewarded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", "level", name="uq_level_reward_student_level"),
    )
    op.create_index("ix_level_rewards_student_id", "level_rewards", ["student_id"])

    op.execute(
        """
        INSERT INTO student_wallet (student_id, coins, xp, level, total_problems_solved, created_at, updated_at)
        SELECT student_id, coins, xp, level, total_problems_solved, created_at, updated_at
        FROM student_gamification
        ON CONFLICT (student_id) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO owned_vehicles (id, student_id, vehicle_id, purchased_at)
        SELECT id, student_id, vehicle_id, purchased_at
        FROM student_vehicles
        ON CONFLICT (student_id, vehicle_id) DO NOTHING
        """
    )
    op.execute(
        """
        UPDATE student_wallet sw
        SET active_vehicle_id = selected.vehicle_id
        FROM (
            SELECT student_id, vehicle_id
            FROM student_vehicles
            WHERE is_selected = true
        ) selected
        WHERE selected.student_id = sw.student_id
        """
    )


def downgrade() -> None:
    op.drop_index("ix_level_rewards_student_id", table_name="level_rewards")
    op.drop_table("level_rewards")
    op.drop_index("ix_owned_vehicles_vehicle_id", table_name="owned_vehicles")
    op.drop_index("ix_owned_vehicles_student_id", table_name="owned_vehicles")
    op.drop_table("owned_vehicles")
    op.drop_table("student_streaks")
    op.drop_index("ix_topic_rewards_topic_id", table_name="topic_rewards")
    op.drop_index("ix_topic_rewards_student_id", table_name="topic_rewards")
    op.drop_table("topic_rewards")
    op.drop_table("student_wallet")
    op.drop_column("vehicles", "type")
    op.drop_column("vehicles", "price")
    op.drop_column("vehicles", "xp_required")
    op.drop_column("vehicles", "level_required")
