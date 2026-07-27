"""add PLUGIN to question_type

Revision ID: 0006_plugin_question
Revises: 0005_add_plugins_table
Create Date: 2026-01-24

"""
from __future__ import annotations

from alembic import op

revision = "0006_plugin_question"
down_revision = "0005_add_plugins_table"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE question_type ADD VALUE IF NOT EXISTS 'PLUGIN'")


def downgrade() -> None:
    pass
