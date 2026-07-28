"""merge_heads

Revision ID: 7e2404835907
Revises: 20260724_remove_virtual_pet, 5f6c7a8b9c0d
Create Date: 2026-07-28 15:09:59.017866

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '7e2404835907'
down_revision = ('20260724_remove_virtual_pet', '5f6c7a8b9c0d')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

