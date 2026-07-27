"""add StudyPoint virtual pet lifecycle

Revision ID: 20260723_virtual_pet
Revises: 20260721_inventory_unique
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260723_virtual_pet"
down_revision = "20260721_inventory_unique"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student_pets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("pet_type", sa.String(40), nullable=False, server_default="cat"),
        sa.Column("pet_name", sa.String(40), nullable=False, server_default="Luna"),
        sa.Column("current_stage", sa.String(40), nullable=False, server_default="egg"),
        sa.Column("growth_xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("happiness", sa.Integer(), nullable=False, server_default="80"),
        sa.Column("hunger", sa.Integer(), nullable=False, server_default="80"),
        sa.Column("hydration", sa.Integer(), nullable=False, server_default="80"),
        sa.Column("health", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("mood", sa.String(40), nullable=False, server_default="egg"),
        sa.Column("is_alive", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("lifecycle_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("last_learning_activity_date", sa.Date()),
        sa.Column("consecutive_active_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("consecutive_missed_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_decay_processed_date", sa.Date()),
        sa.Column("last_fed_at", sa.DateTime(timezone=True)),
        sa.Column("last_watered_at", sa.DateTime(timezone=True)),
        sa.Column("died_at", sa.DateTime(timezone=True)),
        sa.Column("death_reason", sa.String(120)),
        sa.Column("hatch_animation_seen", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("seen_animation_keys", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("total_active_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_learning_goals", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_problems_solved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_student_pets_student_id", "student_pets", ["student_id"])
    op.create_table(
        "pet_lifecycles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lifecycle_number", sa.Integer(), nullable=False),
        sa.Column("pet_type", sa.String(40), nullable=False),
        sa.Column("pet_name", sa.String(40), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        sa.Column("final_stage", sa.String(40)),
        sa.Column("final_growth_xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_active_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_problems_solved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_learning_goals", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("death_reason", sa.String(120)),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.UniqueConstraint("student_id", "lifecycle_number", name="uq_pet_lifecycle_number"),
    )
    op.create_index("ix_pet_lifecycles_student_id", "pet_lifecycles", ["student_id"])
    op.create_table(
        "pet_reward_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("pet_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("student_pets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_key", sa.String(180), nullable=False),
        sa.Column("event_type", sa.String(60), nullable=False),
        sa.Column("growth_xp_delta", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("happiness_delta", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("event_metadata", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("event_key", name="uq_pet_reward_event_key"),
    )
    op.create_index("ix_pet_reward_events_student_id", "pet_reward_events", ["student_id"])
    op.create_index("ix_pet_reward_events_pet_id", "pet_reward_events", ["pet_id"])


def downgrade() -> None:
    op.drop_table("pet_reward_events")
    op.drop_table("pet_lifecycles")
    op.drop_table("student_pets")
