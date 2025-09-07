"""create first db version

Revision ID: dd3ce30a0a72
Revises: 
Create Date: 2025-09-06 11:25:32.612794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dd3ce30a0a72'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """
    Create the 'source' table using a raw SQL block.
    """
    op.execute(
        """
        CREATE TABLE source (
            id SERIAL PRIMARY KEY,
            url TEXT NOT NULL,
            external_id UUID NOT NULL DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def downgrade():
    """
    Drop the 'source' table using a raw SQL block.
    """
    op.execute(
        """
        DROP TABLE source;
        """
    )
