"""Add label column to grades

Revision ID: 0008_add_grade_label
Revises: 0007_topics_table
Create Date: 2026-03-01
"""
from __future__ import annotations

from alembic import op  # type: ignore
import sqlalchemy as sa  # type: ignore


# revision identifiers, used by Alembic.
revision = "0008_add_grade_label"
down_revision = "0007_topics_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("grades", sa.Column("label", sa.String(8), nullable=True))


def downgrade() -> None:
    op.drop_column("grades", "label")
