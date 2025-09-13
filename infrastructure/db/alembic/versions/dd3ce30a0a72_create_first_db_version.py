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
    op.execute(
        """
        CREATE TABLE sources (
            id SERIAL PRIMARY KEY,
            url TEXT NOT NULL,
            external_id UUID NOT NULL DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE feeds (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            external_id UUID NOT NULL DEFAULT gen_random_uuid(),
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE jobs (
            id SERIAL PRIMARY KEY,
            func_name TEXT NOT NULL,
            args TEXT NOT NULL,
            schedule TEXT NOT NULL,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def downgrade():
    op.execute(
        """
        DROP TABLE sources;
        DROP TABLE feeds;
        DROP TABLE jobs;
        """
    )
