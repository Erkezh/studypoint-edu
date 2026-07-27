"""prevent duplicate character inventory purchases

Revision ID: 20260721_inventory_unique
Revises: 20260721_game_path
"""

from alembic import op


revision = "20260721_inventory_unique"
down_revision = "20260721_game_path"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq_user_item_user_item", "user_items", ["user_id", "item_id"])


def downgrade() -> None:
    op.drop_constraint("uq_user_item_user_item", "user_items", type_="unique")
