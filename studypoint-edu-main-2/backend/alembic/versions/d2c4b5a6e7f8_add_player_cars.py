"""add player cars

Revision ID: d2c4b5a6e7f8
Revises: 793dc8fc4bb5
Create Date: 2026-07-04 15:20:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "d2c4b5a6e7f8"
down_revision = "793dc8fc4bb5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "player_cars",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("customization", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_player_cars_user_id"), "player_cars", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_player_cars_user_id"), table_name="player_cars")
    op.drop_table("player_cars")
