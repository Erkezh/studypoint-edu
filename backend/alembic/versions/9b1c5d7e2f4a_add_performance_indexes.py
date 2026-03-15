"""add performance indexes for hot query paths

Revision ID: 9b1c5d7e2f4a
Revises: 82d9dbfdc692
Create Date: 2026-03-15
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "9b1c5d7e2f4a"
down_revision = "82d9dbfdc692"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_users_parent_id", "users", ["parent_id"], unique=False)

    op.create_index(
        "ix_topics_published_order_id",
        "topics",
        ["is_published", "order", "id"],
        unique=False,
    )

    op.create_index(
        "ix_skills_published_subject_grade_code",
        "skills",
        ["is_published", "subject_id", "grade_id", "code"],
        unique=False,
    )

    op.create_index(
        "ix_questions_skill_level_id",
        "questions",
        ["skill_id", "level", "id"],
        unique=False,
    )

    op.create_index(
        "ix_practice_sessions_active_lookup",
        "practice_sessions",
        ["user_id", "skill_id", "last_activity_at"],
        unique=False,
        postgresql_where=sa.text("finished_at IS NULL"),
    )

    op.create_index(
        "ix_practice_attempts_session_question_not_null",
        "practice_attempts",
        ["session_id", "question_id"],
        unique=False,
        postgresql_where=sa.text("question_id IS NOT NULL"),
    )

    op.create_index(
        "ix_practice_attempts_user_skill_answered_at",
        "practice_attempts",
        ["user_id", "skill_id", "answered_at"],
        unique=False,
    )

    op.create_index(
        "ix_practice_attempts_session_answered_at",
        "practice_attempts",
        ["session_id", "answered_at"],
        unique=False,
    )

    op.create_index(
        "ix_progress_snapshots_user_last_practiced_at",
        "progress_snapshots",
        ["user_id", "last_practiced_at"],
        unique=False,
    )

    op.create_index(
        "ix_assignments_classroom_created_at",
        "assignments",
        ["classroom_id", "created_at"],
        unique=False,
    )

    op.create_index(
        "ix_assignment_status_student_assignment",
        "assignment_status",
        ["student_id", "assignment_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_assignment_status_student_assignment", table_name="assignment_status")
    op.drop_index("ix_assignments_classroom_created_at", table_name="assignments")
    op.drop_index("ix_progress_snapshots_user_last_practiced_at", table_name="progress_snapshots")
    op.drop_index("ix_practice_attempts_session_answered_at", table_name="practice_attempts")
    op.drop_index("ix_practice_attempts_user_skill_answered_at", table_name="practice_attempts")
    op.drop_index("ix_practice_attempts_session_question_not_null", table_name="practice_attempts")
    op.drop_index("ix_practice_sessions_active_lookup", table_name="practice_sessions")
    op.drop_index("ix_questions_skill_level_id", table_name="questions")
    op.drop_index("ix_skills_published_subject_grade_code", table_name="skills")
    op.drop_index("ix_topics_published_order_id", table_name="topics")
    op.drop_index("ix_users_parent_id", table_name="users")
