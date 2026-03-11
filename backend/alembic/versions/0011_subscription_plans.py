"""Add FAMILY, CLASSROOM, SCHOOL to subscription_plan enum

Revision ID: 0011_subscription_plans
Revises: 0010_grade_label_nn
Create Date: 2026-03-10
"""
from __future__ import annotations

from alembic import op


# revision identifiers, used by Alembic.
revision = "0011_subscription_plans"
down_revision = "6e10a3659ce6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new enum values to subscription_plan type
    op.execute("ALTER TYPE subscription_plan ADD VALUE IF NOT EXISTS 'FAMILY'")
    op.execute("ALTER TYPE subscription_plan ADD VALUE IF NOT EXISTS 'CLASSROOM'")
    op.execute("ALTER TYPE subscription_plan ADD VALUE IF NOT EXISTS 'SCHOOL'")


def downgrade() -> None:
    # PostgreSQL doesn't support removing enum values easily
    # This would require recreating the type, which is complex
    pass
