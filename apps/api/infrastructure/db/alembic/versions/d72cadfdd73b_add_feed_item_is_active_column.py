"""add feed item is_active column

Revision ID: d72cadfdd73b
Revises: 388f25958b67
Create Date: 2026-01-18 02:04:32.154295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd72cadfdd73b'
down_revision: Union[str, Sequence[str], None] = '388f25958b67'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE feed_items ADD COLUMN is_active BOOLEAN DEFAULT TRUE;")


def downgrade() -> None:
    op.execute("ALTER TABLE feed_items DROP COLUMN is_active;")
