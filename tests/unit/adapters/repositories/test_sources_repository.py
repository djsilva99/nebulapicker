from datetime import datetime
from uuid import uuid4

import psycopg
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.adapters.repositories.sources_repository import SourcesRepository
from src.domain.models.source import Source

# Define PostgreSQL connection constants
# This URL should point to your running local PostgreSQL instance
TEST_DB_URL = "postgresql://postgres:postgres@localhost:5433/"
TEST_DB_NAME = "test_nebula_repo"


@pytest.fixture(scope="session")
def setup_test_db():
    """
    Manages the creation and dropping of the test database for the session.
    """
    # Connect to the default postgres database to create/drop the test database
    with psycopg.connect(TEST_DB_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')
            cur.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')

    test_db_url = f"{TEST_DB_URL}{TEST_DB_NAME}"
    yield test_db_url

    # Teardown: Drop the test database after the session
    with psycopg.connect(TEST_DB_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')


@pytest.fixture
def db_session(setup_test_db):
    """
    Provides a clean, transactional database session for each test.
    """
    engine = create_engine(setup_test_db)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Manually create the schema for the test
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sources (
                id SERIAL PRIMARY KEY,
                external_id TEXT UNIQUE NOT NULL,
                url TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc')
            )
        """))

    session = testing_session_local()

    # Clear all data from the table before each test to ensure a clean state
    session.execute(text("TRUNCATE TABLE sources RESTART IDENTITY CASCADE;"))
    session.commit()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def repo(db_session):
    return SourcesRepository(db_session)


def test_get_by_id_returns_source(repo, db_session):
    # GIVEN
    external_id = str(uuid4())
    db_session.execute(
        text("""
            INSERT INTO sources (external_id, url, name, created_at)
            VALUES (:external_id, :url, :name, :created_at)
        """),
        {
            "external_id": external_id,
            "url": "https://example.com",
            "name": "Example",
            "created_at": datetime(2025, 1, 1, 12, 0, 0),
        }
    )
    db_session.commit()
    inserted_id = db_session.execute(text("SELECT id FROM sources")).scalar_one()

    # WHEN
    source = repo.get_by_id(inserted_id)

    # THEN
    assert source is not None
    assert source.id == inserted_id
    assert str(source.external_id) == external_id
    assert source.url == "https://example.com"
    assert source.name == "Example"


def test_get_all_returns_sources(repo, db_session):
    # GIVEN
    db_session.execute(
        text("""
            INSERT INTO sources (external_id, url, name, created_at)
            VALUES (:external_id, :url, :name, :created_at)
        """),
        {
            "external_id": str(uuid4()),
            "url": "https://example.com/1",
            "name": "Example 1",
            "created_at": datetime(2025, 1, 1, 12, 0, 0),
        }
    )
    db_session.execute(
        text("""
            INSERT INTO sources (external_id, url, name, created_at)
            VALUES (:external_id, :url, :name, :created_at)
        """),
        {
            "external_id": str(uuid4()),
            "url": "https://example.com/2",
            "name": "Example 2",
            "created_at": datetime(2025, 1, 2, 12, 0, 0),
        }
    )
    db_session.commit()

    # WHEN
    sources = repo.get_all()

    # THEN
    assert len(sources) == 2
    assert all(isinstance(s, Source) for s in sources)


def test_get_all_returns_empty(repo, db_session):
    # WHEN
    sources = repo.get_all()

    # THEN
    assert len(sources) == 0


def test_get_by_id_returns_none_when_not_found(repo, db_session):
    # WHEN
    source = repo.get_by_id(999)

    # THEN
    assert source is None
