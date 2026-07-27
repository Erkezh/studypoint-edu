"""add level column to quiz_questions

Revision ID: 5f6c7a8b9c0d
Revises: 03f7a6b914a3
Create Date: 2026-07-22 11:15:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f6c7a8b9c0d'
down_revision = '03f7a6b914a3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('quiz_questions', sa.Column('level', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('quiz_questions', 'level')
