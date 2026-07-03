"""add read attribute in feed items

Revision ID: 57769d4c95de
Revises: 2240010abc8d
Create Date: 2026-06-19 23:33:10.723169

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57769d4c95de'
down_revision: Union[str, Sequence[str], None] = '2240010abc8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE feed_items ADD COLUMN read BOOLEAN DEFAULT FALSE;")


def downgrade() -> None:
    op.execute("ALTER TABLE feed_items DROP COLUMN read;")
