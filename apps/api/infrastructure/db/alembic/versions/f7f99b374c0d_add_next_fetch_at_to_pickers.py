"""add next_fetch_at to pickers

Revision ID: f7f99b374c0d
Revises: eb60f5570ef5
Create Date: 2026-09-11 00:51:00.962471

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7f99b374c0d'
down_revision: Union[str, Sequence[str], None] = 'eb60f5570ef5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE pickers
        ADD COLUMN next_fetch TIMESTAMP WITH TIME ZONE
    """)


def downgrade() -> None:
    op.execute("""
        ALTER TABLE pickers
        DROP COLUMN next_fetch
    """)
