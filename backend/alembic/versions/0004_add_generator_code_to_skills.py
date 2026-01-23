"""add generator_code to skills

Revision ID: 0004_generator_code
Revises: 0003_interactive
Create Date: 2026-01-20
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0004_generator_code"
down_revision = "0003_interactive"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поле generator_code для хранения кода генератора
    op.add_column("skills", sa.Column("generator_code", sa.Text(), nullable=True))
    
    # Добавляем поле generator_metadata для хранения метаданных генератора
    op.add_column(
        "skills",
        sa.Column(
            "generator_metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb")
        )
    )


def downgrade() -> None:
    op.drop_column("skills", "generator_metadata")
    op.drop_column("skills", "generator_code")
