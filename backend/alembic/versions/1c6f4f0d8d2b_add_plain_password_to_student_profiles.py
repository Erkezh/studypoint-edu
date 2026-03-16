"""Add plain_password column to student_profiles.

Revision ID: 1c6f4f0d8d2b
Revises: f0b8f6e2c1aa
Create Date: 2026-03-16 11:20:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1c6f4f0d8d2b"
down_revision = "f0b8f6e2c1aa"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("student_profiles", sa.Column("plain_password", sa.String(length=128), nullable=True))


def downgrade() -> None:
    op.drop_column("student_profiles", "plain_password")
