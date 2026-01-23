"""ixl practice timer scoring reports

Revision ID: 0002_ixl_practice
Revises: 0001_initial
Create Date: 2026-01-16
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0002_ixl_practice"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE TYPE practice_zone AS ENUM ('LEARNING','REFINING','CHALLENGE');")
    op.execute("CREATE TYPE mistake_type AS ENUM ('WRONG','INVALID_FORMAT','TIMEOUT');")

    op.add_column("practice_sessions", sa.Column("current_smartscore", sa.Integer(), server_default="0", nullable=False))
    op.add_column("practice_sessions", sa.Column("best_smartscore", sa.Integer(), server_default="0", nullable=False))
    op.add_column("practice_sessions", sa.Column("total_questions_answered", sa.Integer(), server_default="0", nullable=False))
    op.add_column("practice_sessions", sa.Column("total_correct", sa.Integer(), server_default="0", nullable=False))
    op.add_column("practice_sessions", sa.Column("total_incorrect", sa.Integer(), server_default="0", nullable=False))
    op.add_column("practice_sessions", sa.Column("current_streak_correct", sa.Integer(), server_default="0", nullable=False))
    op.add_column("practice_sessions", sa.Column("max_streak_correct", sa.Integer(), server_default="0", nullable=False))
    op.add_column("practice_sessions", sa.Column("current_zone", sa.Enum(name="practice_zone"), server_default="LEARNING", nullable=False))
    op.add_column("practice_sessions", sa.Column("last_question_id", sa.Integer(), nullable=True))
    op.add_column("practice_sessions", sa.Column("last_activity_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False))
    op.add_column("practice_sessions", sa.Column("active_time_seconds", sa.Integer(), server_default="0", nullable=False))
    op.add_column("practice_sessions", sa.Column("inactivity_threshold_seconds", sa.Integer(), server_default="240", nullable=False))
    op.create_index("ix_practice_sessions_current_zone", "practice_sessions", ["current_zone"], unique=False)

    op.add_column("practice_attempts", sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("practice_attempts", sa.Column("skill_id", sa.Integer(), nullable=True))
    op.add_column("practice_attempts", sa.Column("question_level", sa.Integer(), server_default="1", nullable=False))
    op.add_column("practice_attempts", sa.Column("question_payload", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False))
    op.add_column("practice_attempts", sa.Column("mistake_type", sa.Enum(name="mistake_type"), nullable=True))
    op.add_column("practice_attempts", sa.Column("hints_used_count", sa.Integer(), server_default="0", nullable=False))
    op.add_column("practice_attempts", sa.Column("explanation_viewed", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("practice_attempts", sa.Column("smartscore_before", sa.Integer(), server_default="0", nullable=False))
    op.add_column("practice_attempts", sa.Column("smartscore_after", sa.Integer(), server_default="0", nullable=False))
    op.add_column("practice_attempts", sa.Column("zone_before", sa.Enum(name="practice_zone"), server_default="LEARNING", nullable=False))
    op.add_column("practice_attempts", sa.Column("zone_after", sa.Enum(name="practice_zone"), server_default="LEARNING", nullable=False))
    op.create_index("ix_practice_attempts_user_id", "practice_attempts", ["user_id"], unique=False)
    op.create_index("ix_practice_attempts_skill_id", "practice_attempts", ["skill_id"], unique=False)

    # Backfill user_id/skill_id for existing rows (if any)
    op.execute(
        """
        UPDATE practice_attempts pa
        SET user_id = ps.user_id,
            skill_id = ps.skill_id
        FROM practice_sessions ps
        WHERE pa.session_id = ps.id AND (pa.user_id IS NULL OR pa.skill_id IS NULL);
        """
    )
    op.alter_column("practice_attempts", "user_id", nullable=False)
    op.alter_column("practice_attempts", "skill_id", nullable=False)
    op.create_foreign_key("fk_practice_attempts_user_id", "practice_attempts", "users", ["user_id"], ["id"], ondelete="CASCADE")
    op.create_foreign_key("fk_practice_attempts_skill_id", "practice_attempts", "skills", ["skill_id"], ["id"], ondelete="CASCADE")

    op.add_column("progress_snapshots", sa.Column("best_smartscore_all_time", sa.Integer(), server_default="0", nullable=False))
    op.add_column("progress_snapshots", sa.Column("total_questions_answered_all_time", sa.Integer(), server_default="0", nullable=False))
    op.add_column("progress_snapshots", sa.Column("total_time_seconds_all_time", sa.Integer(), server_default="0", nullable=False))

    op.add_column("assignments", sa.Column("target_smartscore", sa.Integer(), server_default="80", nullable=False))
    op.add_column("assignment_status", sa.Column("time_spent_seconds", sa.Integer(), server_default="0", nullable=False))
    op.add_column("assignment_status", sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "award_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("related_session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_award_events_user_id", "award_events", ["user_id"], unique=False)
    op.create_index("ix_award_events_skill_id", "award_events", ["skill_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_award_events_skill_id", table_name="award_events")
    op.drop_index("ix_award_events_user_id", table_name="award_events")
    op.drop_table("award_events")

    op.drop_column("assignment_status", "last_activity_at")
    op.drop_column("assignment_status", "time_spent_seconds")
    op.drop_column("assignments", "target_smartscore")

    op.drop_column("progress_snapshots", "total_time_seconds_all_time")
    op.drop_column("progress_snapshots", "total_questions_answered_all_time")
    op.drop_column("progress_snapshots", "best_smartscore_all_time")

    op.drop_constraint("fk_practice_attempts_skill_id", "practice_attempts", type_="foreignkey")
    op.drop_constraint("fk_practice_attempts_user_id", "practice_attempts", type_="foreignkey")
    op.drop_index("ix_practice_attempts_skill_id", table_name="practice_attempts")
    op.drop_index("ix_practice_attempts_user_id", table_name="practice_attempts")
    op.drop_column("practice_attempts", "zone_after")
    op.drop_column("practice_attempts", "zone_before")
    op.drop_column("practice_attempts", "smartscore_after")
    op.drop_column("practice_attempts", "smartscore_before")
    op.drop_column("practice_attempts", "explanation_viewed")
    op.drop_column("practice_attempts", "hints_used_count")
    op.drop_column("practice_attempts", "mistake_type")
    op.drop_column("practice_attempts", "question_payload")
    op.drop_column("practice_attempts", "question_level")
    op.drop_column("practice_attempts", "skill_id")
    op.drop_column("practice_attempts", "user_id")

    op.drop_index("ix_practice_sessions_current_zone", table_name="practice_sessions")
    op.drop_column("practice_sessions", "inactivity_threshold_seconds")
    op.drop_column("practice_sessions", "active_time_seconds")
    op.drop_column("practice_sessions", "last_activity_at")
    op.drop_column("practice_sessions", "last_question_id")
    op.drop_column("practice_sessions", "current_zone")
    op.drop_column("practice_sessions", "max_streak_correct")
    op.drop_column("practice_sessions", "current_streak_correct")
    op.drop_column("practice_sessions", "total_incorrect")
    op.drop_column("practice_sessions", "total_correct")
    op.drop_column("practice_sessions", "total_questions_answered")
    op.drop_column("practice_sessions", "best_smartscore")
    op.drop_column("practice_sessions", "current_smartscore")

    op.execute("DROP TYPE mistake_type;")
    op.execute("DROP TYPE practice_zone;")
