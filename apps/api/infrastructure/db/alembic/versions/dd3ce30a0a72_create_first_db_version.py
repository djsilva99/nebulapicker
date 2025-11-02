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
            name TEXT,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE feeds (
            id SERIAL PRIMARY KEY,
            name TEXT,
            external_id UUID NOT NULL DEFAULT gen_random_uuid(),
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE feed_items (
            id SERIAL PRIMARY KEY,
            title TEXT,
            description TEXT,
            link TEXT,
            author TEXT,
            feed_id INT NOT NULL REFERENCES feeds(id),
            external_id UUID NOT NULL DEFAULT gen_random_uuid(),
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE pickers (
            id SERIAL PRIMARY KEY,
            external_id UUID NOT NULL DEFAULT gen_random_uuid(),
            source_id INT NOT NULL REFERENCES sources(id),
            feed_id INT NOT NULL REFERENCES feeds(id),
            cronjob TEXT,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TYPE operation AS ENUM (
            'identity', 
            'title_contains', 
            'description_contains',
            'title_does_not_contain',
            'description_does_not_contain'
        );

        CREATE TABLE filters (
            id SERIAL PRIMARY KEY,
            picker_id INT NOT NULL REFERENCES pickers(id),
            operation operation NOT NULL,
            args TEXT,
            created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
    )


def downgrade():
    op.execute(
        """
        DROP TABLE filters;
        DROP TABLE pickers;
        DROP TABLE sources;
        DROP TABLE feed_items;
        DROP TABLE feeds;
        DROP TYPE operation;
        """
    )
