"""add_plugins_table

Revision ID: 0005_add_plugins_table
Revises: 0004_add_generator_code_to_skills
Create Date: 2026-01-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0005_add_plugins_table"
down_revision = "b9d78e3eeff1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "plugins",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True, nullable=False),
        sa.Column("plugin_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("version", sa.String(length=32), nullable=False),
        sa.Column("entry", sa.String(length=255), nullable=False),
        sa.Column("api_version", sa.String(length=16), nullable=False, server_default="1"),
        sa.Column("capabilities", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("height", sa.Integer(), nullable=False, server_default="400"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("manifest_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_plugins_name", "plugins", ["name"], unique=False)
    op.create_index("ix_plugins_plugin_id", "plugins", ["plugin_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_plugins_plugin_id", table_name="plugins")
    op.drop_index("ix_plugins_name", table_name="plugins")
    op.drop_table("plugins")
