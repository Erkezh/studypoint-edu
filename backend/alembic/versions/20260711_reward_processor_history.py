"""reward processor history

Revision ID: 20260711_reward_history
Revises: 20260708_balanced_gamification
Create Date: 2026-07-11 00:00:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260711_reward_history"
down_revision = "20260708_balanced_gamification"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("student_streaks", sa.Column("longest_streak", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("student_streaks", sa.Column("streak_started_at", sa.Date(), nullable=True))
    op.add_column("student_streaks", sa.Column("streak_sequence_id", sa.String(length=80), nullable=True))
    op.execute("UPDATE student_streaks SET longest_streak = GREATEST(current_streak, 0)")
    op.execute(
        """
        UPDATE student_streaks
        SET streak_started_at = last_active_date - (GREATEST(current_streak, 1) - 1),
            streak_sequence_id = student_id::text || ':' || COALESCE(last_active_date::text, 'seed')
        WHERE current_streak > 0 AND last_active_date IS NOT NULL
        """
    )

    op.create_table(
        "streak_rewards",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("streak_sequence_id", sa.String(length=80), nullable=False),
        sa.Column("cycle_number", sa.Integer(), nullable=False),
        sa.Column("rewarded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", "streak_sequence_id", "cycle_number", name="uq_streak_reward_sequence_cycle"),
    )
    op.create_index("ix_streak_rewards_student_id", "streak_rewards", ["student_id"])

    op.create_table(
        "wallet_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_type", sa.String(length=80), nullable=False),
        sa.Column("xp_change", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("coin_change", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("xp_balance_after", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("coin_balance_after", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("reference_type", sa.String(length=80), nullable=True),
        sa.Column("reference_id", sa.String(length=120), nullable=True),
        sa.Column("transaction_metadata", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_wallet_transactions_student_id", "wallet_transactions", ["student_id"])

    op.create_table(
        "reward_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("idempotency_key", sa.String(length=160), nullable=False),
        sa.Column("reference_type", sa.String(length=80), nullable=True),
        sa.Column("reference_id", sa.String(length=120), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("xp_awarded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("coins_awarded", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("result", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key", name="uq_reward_event_idempotency_key"),
    )
    op.create_index("ix_reward_events_student_id", "reward_events", ["student_id"])


def downgrade() -> None:
    op.drop_index("ix_reward_events_student_id", table_name="reward_events")
    op.drop_table("reward_events")
    op.drop_index("ix_wallet_transactions_student_id", table_name="wallet_transactions")
    op.drop_table("wallet_transactions")
    op.drop_index("ix_streak_rewards_student_id", table_name="streak_rewards")
    op.drop_table("streak_rewards")
    op.drop_column("student_streaks", "streak_sequence_id")
    op.drop_column("student_streaks", "streak_started_at")
    op.drop_column("student_streaks", "longest_streak")
