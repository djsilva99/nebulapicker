"""create starred read column

Revision ID: eb60f5570ef5
Revises: 4d806b3d39b5
Create Date: 2026-07-27 01:45:52.564944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb60f5570ef5'
down_revision: Union[str, Sequence[str], None] = '4d806b3d39b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE feed_items ADD COLUMN starred_read BOOLEAN NOT NULL DEFAULT FALSE;")


def downgrade() -> None:
    op.execute("ALTER TABLE feed_items DROP COLUMN starred_read;")
