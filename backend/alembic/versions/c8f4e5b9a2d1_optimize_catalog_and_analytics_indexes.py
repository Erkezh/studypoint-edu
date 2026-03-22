"""optimize catalog and analytics indexes

Revision ID: c8f4e5b9a2d1
Revises: 1c6f4f0d8d2b
Create Date: 2026-03-22
"""

from __future__ import annotations

from alembic import op


# revision identifiers, used by Alembic.
revision = "c8f4e5b9a2d1"
down_revision = "1c6f4f0d8d2b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_skills_published_grade_topic_code",
        "skills",
        ["is_published", "grade_id", "topic_id", "code"],
        unique=False,
    )
    op.create_index(
        "ix_practice_sessions_user_skill",
        "practice_sessions",
        ["user_id", "skill_id"],
        unique=False,
    )
    op.create_index(
        "ix_practice_attempts_user_answered_at",
        "practice_attempts",
        ["user_id", "answered_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_practice_attempts_user_answered_at", table_name="practice_attempts")
    op.drop_index("ix_practice_sessions_user_skill", table_name="practice_sessions")
    op.drop_index("ix_skills_published_grade_topic_code", table_name="skills")
