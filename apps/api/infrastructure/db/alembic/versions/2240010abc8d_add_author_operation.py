"""add author does not contain operation

Revision ID: 2240010abc8d
Revises: 294c820cfdad
Create Date: 2026-06-10 13:27:11.014646

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2240010abc8d'
down_revision: Union[str, Sequence[str], None] = '294c820cfdad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE operation ADD VALUE IF NOT EXISTS 'author_does_not_contain'")


def downgrade() -> None:
    # ENUM value removal is not safe; downgrade intentionally left empty.
    pass
