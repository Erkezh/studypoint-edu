"""add student gamification loop

Revision ID: e4f6a1b2c3d4
Revises: d2c4b5a6e7f8
Create Date: 2026-07-07 15:30:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "e4f6a1b2c3d4"
down_revision = "d2c4b5a6e7f8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "student_gamification",
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("xp", sa.Integer(), server_default="0", nullable=False),
        sa.Column("coins", sa.Integer(), server_default="0", nullable=False),
        sa.Column("level", sa.Integer(), server_default="1", nullable=False),
        sa.Column("combo_streak", sa.Integer(), server_default="0", nullable=False),
        sa.Column("daily_streak", sa.Integer(), server_default="0", nullable=False),
        sa.Column("last_streak_date", sa.Date(), nullable=True),
        sa.Column("total_problems_solved", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("student_id"),
    )

    op.create_table(
        "vehicles",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("unlock_level", sa.Integer(), server_default="1", nullable=False),
        sa.Column("unlock_xp", sa.Integer(), server_default="0", nullable=False),
        sa.Column("coin_price", sa.Integer(), server_default="0", nullable=False),
        sa.Column("model_url", sa.String(length=255), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "garage_items",
        sa.Column("id", sa.String(length=100), nullable=False),
        sa.Column("vehicle_type", sa.String(length=80), server_default="all", nullable=False),
        sa.Column("item_type", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("coin_price", sa.Integer(), server_default="0", nullable=False),
        sa.Column("unlock_level", sa.Integer(), server_default="1", nullable=False),
        sa.Column("model_url", sa.String(length=255), nullable=True),
        sa.Column("thumbnail_url", sa.String(length=255), nullable=True),
        sa.Column("rarity", sa.String(length=50), server_default="common", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    op.create_table(
        "student_vehicles",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("vehicle_id", sa.String(length=80), nullable=False),
        sa.Column("purchased_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_selected", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", "vehicle_id", name="uq_student_vehicle"),
    )
    op.create_index(op.f("ix_student_vehicles_student_id"), "student_vehicles", ["student_id"], unique=False)
    op.create_index(op.f("ix_student_vehicles_vehicle_id"), "student_vehicles", ["vehicle_id"], unique=False)

    op.create_table(
        "student_garage_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("garage_item_id", sa.String(length=100), nullable=False),
        sa.Column("purchased_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["garage_item_id"], ["garage_items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", "garage_item_id", name="uq_student_garage_item"),
    )
    op.create_index(op.f("ix_student_garage_items_student_id"), "student_garage_items", ["student_id"], unique=False)

    op.create_table(
        "selected_vehicle_customization",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("student_id", sa.UUID(), nullable=False),
        sa.Column("vehicle_id", sa.String(length=80), nullable=False),
        sa.Column("wheel_item_id", sa.String(length=100), nullable=True),
        sa.Column("paint_item_id", sa.String(length=100), nullable=True),
        sa.Column("roof_item_id", sa.String(length=100), nullable=True),
        sa.Column("spoiler_item_id", sa.String(length=100), nullable=True),
        sa.Column("headlight_item_id", sa.String(length=100), nullable=True),
        sa.Column("sticker_item_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["wheel_item_id"], ["garage_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["paint_item_id"], ["garage_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["roof_item_id"], ["garage_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["spoiler_item_id"], ["garage_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["headlight_item_id"], ["garage_items.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sticker_item_id"], ["garage_items.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", "vehicle_id", name="uq_student_vehicle_customization"),
    )
    op.create_index(op.f("ix_selected_vehicle_customization_student_id"), "selected_vehicle_customization", ["student_id"], unique=False)
    op.create_index(op.f("ix_selected_vehicle_customization_vehicle_id"), "selected_vehicle_customization", ["vehicle_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_selected_vehicle_customization_vehicle_id"), table_name="selected_vehicle_customization")
    op.drop_index(op.f("ix_selected_vehicle_customization_student_id"), table_name="selected_vehicle_customization")
    op.drop_table("selected_vehicle_customization")
    op.drop_index(op.f("ix_student_garage_items_student_id"), table_name="student_garage_items")
    op.drop_table("student_garage_items")
    op.drop_index(op.f("ix_student_vehicles_vehicle_id"), table_name="student_vehicles")
    op.drop_index(op.f("ix_student_vehicles_student_id"), table_name="student_vehicles")
    op.drop_table("student_vehicles")
    op.drop_table("garage_items")
    op.drop_table("vehicles")
    op.drop_table("student_gamification")
