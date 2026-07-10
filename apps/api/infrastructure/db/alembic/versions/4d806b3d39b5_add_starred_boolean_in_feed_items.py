"""add starred boolean in feed items

Revision ID: 4d806b3d39b5
Revises: 57769d4c95de
Create Date: 2026-07-06 00:35:57.955283

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d806b3d39b5'
down_revision: Union[str, Sequence[str], None] = '57769d4c95de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE feed_items ADD COLUMN is_starred BOOLEAN DEFAULT FALSE;")


def downgrade() -> None:
    op.execute("ALTER TABLE feed_items DROP COLUMN is_starred;")
