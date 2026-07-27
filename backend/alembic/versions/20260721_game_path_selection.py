"""add game path selection

Revision ID: 20260721_game_path
Revises: 20260711_reward_history
"""

from alembic import op
import sqlalchemy as sa


revision = "20260721_game_path"
down_revision = "20260711_reward_history"
branch_labels = None
depends_on = None


game_type = sa.Enum("car", "character", name="game_type")


def upgrade() -> None:
    game_type.create(op.get_bind(), checkfirst=True)
    op.add_column("student_profiles", sa.Column("active_game", game_type, nullable=True))
    op.add_column("student_profiles", sa.Column("game_selected_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("student_profiles", sa.Column("last_game_switch_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("shop_items", sa.Column("game_type", game_type, nullable=True))
    op.add_column("shop_items", sa.Column("category", sa.String(length=80), nullable=True))
    op.add_column("shop_items", sa.Column("required_level", sa.Integer(), nullable=True))
    op.execute("UPDATE shop_items SET game_type = 'character', category = COALESCE(type, 'accessories'), required_level = 1")
    op.alter_column("shop_items", "game_type", nullable=False)
    op.alter_column("shop_items", "category", nullable=False)
    op.alter_column("shop_items", "required_level", nullable=False)


def downgrade() -> None:
    op.drop_column("shop_items", "required_level")
    op.drop_column("shop_items", "category")
    op.drop_column("shop_items", "game_type")
    op.drop_column("student_profiles", "last_game_switch_at")
    op.drop_column("student_profiles", "game_selected_at")
    op.drop_column("student_profiles", "active_game")
    game_type.drop(op.get_bind(), checkfirst=True)
