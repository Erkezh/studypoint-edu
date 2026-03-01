"""Add description column to grades

Revision ID: 0009_add_grade_desc
Revises: 0008_add_grade_label
Create Date: 2026-03-01
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0009_add_grade_desc"
down_revision = "0008_add_grade_label"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("grades", sa.Column("description", sa.Text(), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("grades", "description")
