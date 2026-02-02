"""add updated_at column in feeds table

Revision ID: 294c820cfdad
Revises: d72cadfdd73b
Create Date: 2026-01-23 12:13:17.287627

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '294c820cfdad'
down_revision: Union[str, Sequence[str], None] = 'd72cadfdd73b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE feeds ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;")


def downgrade() -> None:
    op.execute("ALTER TABLE feeds DROP COLUMN updated_at;")
