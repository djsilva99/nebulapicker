"""create_image_url_in_feed_items_table

Revision ID: 388f25958b67
Revises: 38977cc5cf52
Create Date: 2026-01-16 16:33:45.369080

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '388f25958b67'
down_revision: Union[str, Sequence[str], None] = '38977cc5cf52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE feed_items ADD COLUMN image_url TEXT DEFAULT NULL;")


def downgrade() -> None:
    op.execute("ALTER TABLE feed_items DROP COLUMN image_url;")
