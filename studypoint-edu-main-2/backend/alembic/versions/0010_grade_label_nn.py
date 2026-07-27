"""Make grade label NOT NULL

Revision ID: 0010_grade_label_nn
Revises: 0009_add_grade_desc
Create Date: 2026-03-01
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0010_grade_label_nn"
down_revision = "0009_add_grade_desc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Fill any NULL labels with the grade number as string
    op.execute("UPDATE grades SET label = CAST(number AS VARCHAR(8)) WHERE label IS NULL")
    op.alter_column("grades", "label", existing_type=sa.String(8), nullable=False)


def downgrade() -> None:
    op.alter_column("grades", "label", existing_type=sa.String(8), nullable=True)
