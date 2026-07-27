"""add interactive to question_type

Revision ID: 0003_interactive
Revises: 0002_ixl_practice
Create Date: 2026-01-20
"""

from __future__ import annotations

from alembic import op


revision = "0003_interactive"
down_revision = "0002_ixl_practice"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем значение INTERACTIVE в enum question_type
    op.execute("ALTER TYPE question_type ADD VALUE IF NOT EXISTS 'INTERACTIVE'")


def downgrade() -> None:
    # В PostgreSQL нельзя удалить значение из enum напрямую
    # Нужно пересоздать enum, что требует удаления всех зависимых данных
    # Поэтому downgrade не реализован - это breaking change
    pass
