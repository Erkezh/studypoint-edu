"""Add topics table and topic_id to skills

Revision ID: 0007_topics_table
Revises: 0006_plugin_question
Create Date: 2026-02-09
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0007_topics_table"
down_revision = "0006_plugin_question"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create topics table
    op.create_table(
        "topics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("icon", sa.String(64), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_topics_slug"), "topics", ["slug"], unique=True)

    # Add topic_id column to skills table
    op.add_column("skills", sa.Column("topic_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_skills_topic_id"), "skills", ["topic_id"], unique=False)
    op.create_foreign_key(
        "fk_skills_topic_id",
        "skills",
        "topics",
        ["topic_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # Remove topic_id from skills
    op.drop_constraint("fk_skills_topic_id", "skills", type_="foreignkey")
    op.drop_index(op.f("ix_skills_topic_id"), table_name="skills")
    op.drop_column("skills", "topic_id")

    # Drop topics table
    op.drop_index(op.f("ix_topics_slug"), table_name="topics")
    op.drop_table("topics")
