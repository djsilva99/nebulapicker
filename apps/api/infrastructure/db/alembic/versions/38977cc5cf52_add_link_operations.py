"""add link operations

Revision ID: 38977cc5cf52
Revises: dd3ce30a0a72
Create Date: 2025-12-11 01:27:20.433782

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '38977cc5cf52'
down_revision: Union[str, Sequence[str], None] = 'dd3ce30a0a72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE operation ADD VALUE IF NOT EXISTS 'link_contains'")
    op.execute("ALTER TYPE operation ADD VALUE IF NOT EXISTS 'link_does_not_contain'")


def downgrade() -> None:
    # ENUM value removal is not safe; downgrade intentionally left empty.
    pass
