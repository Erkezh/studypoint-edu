"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-15
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("ADMIN", "TEACHER", "STUDENT", "PARENT", name="user_role"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role", "users", ["role"], unique=False)

    op.create_table(
        "student_profiles",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("grade_level", sa.Integer(), nullable=False),
        sa.Column("school", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_subjects_slug", "subjects", ["slug"], unique=True)

    op.create_table(
        "grades",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_grades_number", "grades", ["number"], unique=True)

    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("grade_id", sa.Integer(), sa.ForeignKey("grades.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("tags", postgresql.ARRAY(sa.String(length=64)), nullable=False, server_default="{}"),
        sa.Column("difficulty", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("example_url", sa.String(length=1024), nullable=True),
        sa.Column("video_url", sa.String(length=1024), nullable=True),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("subject_id", "grade_id", "code", name="uq_skill_code_grade_subject"),
    )
    op.create_index("ix_skills_subject_id", "skills", ["subject_id"], unique=False)
    op.create_index("ix_skills_grade_id", "skills", ["grade_id"], unique=False)

    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Enum("MCQ", "NUMERIC", "TEXT", "MULTI_SELECT", name="question_type"), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("correct_answer", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("explanation", sa.Text(), nullable=False, server_default=""),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_questions_skill_id", "questions", ["skill_id"], unique=False)
    op.create_index("ix_questions_level", "questions", ["level"], unique=False)

    op.create_table(
        "practice_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("questions_answered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wrong_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("smartscore", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("time_elapsed_sec", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("state", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index("ix_practice_sessions_user_id", "practice_sessions", ["user_id"], unique=False)
    op.create_index("ix_practice_sessions_skill_id", "practice_sessions", ["skill_id"], unique=False)

    op.create_table(
        "practice_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("practice_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", sa.Integer(), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("submitted_answer", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_correct", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("time_spent_sec", sa.Integer(), nullable=False, server_default="0"),
        sa.UniqueConstraint("session_id", "question_id", name="uq_attempt_session_question"),
    )
    op.create_index("ix_practice_attempts_session_id", "practice_attempts", ["session_id"], unique=False)
    op.create_index("ix_practice_attempts_question_id", "practice_attempts", ["question_id"], unique=False)

    op.create_table(
        "progress_snapshots",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("best_smartscore", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_smartscore", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_practiced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_questions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("accuracy_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "classrooms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("teacher_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("grade_id", sa.Integer(), sa.ForeignKey("grades.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_classrooms_teacher_id", "classrooms", ["teacher_id"], unique=False)
    op.create_index("ix_classrooms_grade_id", "classrooms", ["grade_id"], unique=False)

    op.create_table(
        "enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("classroom_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("enrolled_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("classroom_id", "student_id", name="uq_enrollment_class_student"),
    )
    op.create_index("ix_enrollments_classroom_id", "enrollments", ["classroom_id"], unique=False)
    op.create_index("ix_enrollments_student_id", "enrollments", ["student_id"], unique=False)

    op.create_table(
        "assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("classroom_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("classrooms.id", ondelete="CASCADE"), nullable=False),
        sa.Column("skill_id", sa.Integer(), sa.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_assignments_classroom_id", "assignments", ["classroom_id"], unique=False)
    op.create_index("ix_assignments_skill_id", "assignments", ["skill_id"], unique=False)

    op.create_table(
        "assignment_status",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("assignment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.Enum("NOT_STARTED", "IN_PROGRESS", "COMPLETED", name="assignment_status_enum"), nullable=False),
        sa.Column("best_smartscore", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_smartscore", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("questions_answered", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("assignment_id", "student_id", name="uq_assignment_student"),
    )
    op.create_index("ix_assignment_status_assignment_id", "assignment_status", ["assignment_id"], unique=False)
    op.create_index("ix_assignment_status_student_id", "assignment_status", ["student_id"], unique=False)

    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan", sa.Enum("FREE", "PREMIUM", name="subscription_plan"), nullable=False),
        sa.Column("active_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("provider", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", name="uq_subscription_user"),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_table("assignment_status")
    op.drop_table("assignments")
    op.drop_table("enrollments")
    op.drop_table("classrooms")

    op.drop_table("progress_snapshots")
    op.drop_table("practice_attempts")
    op.drop_table("practice_sessions")
    op.drop_table("questions")
    op.drop_table("skills")
    op.drop_table("grades")
    op.drop_table("subjects")
    op.drop_table("student_profiles")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.execute("DROP TYPE IF EXISTS subscription_plan;")
    op.execute("DROP TYPE IF EXISTS assignment_status_enum;")
    op.execute("DROP TYPE IF EXISTS question_type;")
    op.execute("DROP TYPE IF EXISTS user_role;")

