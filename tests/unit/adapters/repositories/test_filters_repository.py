from datetime import datetime

import psycopg
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.adapters.repositories.filters_repository import FiltersRepository
from src.domain.models.filter import FilterRequest, Operation

TEST_DB_URL = "postgresql://postgres:postgres@localhost:5433/"
TEST_DB_NAME = "test_nebula_repo"


@pytest.fixture(scope="session")
def setup_test_db():
    """Create and drop the test database (once per session)."""
    with psycopg.connect(TEST_DB_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')
            cur.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')

    test_db_url = f"{TEST_DB_URL}{TEST_DB_NAME}"

    # Setup schema once
    engine = create_engine(test_db_url)
    with engine.begin() as conn:
        conn.execute(text("""
            DO $$
            BEGIN
                CREATE TYPE operations AS ENUM ('identity');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;

            CREATE TABLE IF NOT EXISTS sources (
                id SERIAL PRIMARY KEY,
                url TEXT NOT NULL,
                external_id UUID NOT NULL DEFAULT gen_random_uuid(),
                name TEXT,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS feeds (
                id SERIAL PRIMARY KEY,
                name TEXT,
                external_id UUID NOT NULL DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS pickers (
                id SERIAL PRIMARY KEY,
                external_id UUID NOT NULL DEFAULT gen_random_uuid(),
                source_id INT NOT NULL REFERENCES sources(id),
                feed_id INT NOT NULL REFERENCES feeds(id),
                cronjob TEXT,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS filters (
                id SERIAL PRIMARY KEY,
                picker_id INT NOT NULL REFERENCES pickers(id),
                operation operations NOT NULL,
                args TEXT,
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))

    yield test_db_url

    # Drop the test database after the session
    with psycopg.connect(TEST_DB_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')


@pytest.fixture
def db_session(setup_test_db):
    """Provide a clean database session for each test."""
    engine = create_engine(setup_test_db)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = testing_session_local()

    # Truncate all tables to reset state
    session.execute(
        text(
            "TRUNCATE TABLE filters, pickers, feeds, sources "
            "RESTART IDENTITY CASCADE;"
        )
    )
    session.commit()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def filters_repo(db_session):
    return FiltersRepository(db_session)



def test_create_inserts_filter_and_returns_model(db_session, filters_repo):
    # GIVEN
    filter_request = FilterRequest(
        picker_id=1,
        operation=Operation("identity"),
        args="[a, b]"
    )

    db_session.execute(
        text(
            "INSERT INTO feeds (id, name)"
            "VALUES (1, 'feed_fake_name')"
        )
    )
    db_session.execute(
        text(
            "INSERT INTO sources (id, url)"
            "VALUES (1, 'www.fake_source.com/feed')"
        )
    )
    db_session.execute(
        text(
            "INSERT INTO pickers (source_id, feed_id, cronjob)"
            "VALUES (1, 1, 'teste')"
        )
    )
    db_session.commit()

    # WHEN
    created = filters_repo.create(filter_request)

    # THEN
    assert created.id is not None
    assert created.picker_id == 1
    assert created.operation == "identity"
    assert created.args == '[a, b]'
    assert isinstance(created.created_at, datetime)
    row = db_session.execute(
        text(
            "SELECT * FROM filters WHERE id = :id"
        ),
        {
            "id": created.id
        }
    ).first()
    assert row is not None


def test_get_by_picker_id_returns_filters(db_session, filters_repo):
    # GIVEN
    db_session.execute(
        text(
            "INSERT INTO feeds (id, name)"
            "VALUES (1, 'feed_fake_name')"
        )
    )
    db_session.execute(
        text(
            "INSERT INTO sources (id, url)"
            "VALUES (1, 'www.fake_source.com/feed')"
        )
    )
    db_session.execute(
        text(
            "INSERT INTO pickers (source_id, feed_id, cronjob)"
            "VALUES (1, 1, 'teste')"
        )
    )
    db_session.execute(
        text("""
            INSERT INTO filters (picker_id, operation, args, created_at)
            VALUES (:picker_id, :operation, :args, :created_at)
        """),
        {
            "picker_id": 1,
            "operation": "identity",
            "args": "['x','y']",
            "created_at": datetime(2025, 1, 1, 12, 0, 0),
        }
    )
    db_session.commit()

    # WHEN
    results = filters_repo.get_by_picker_id(1)

    # THEN
    assert len(results) == 1
    filter_obj = results[0]
    assert filter_obj.picker_id == 1
    assert filter_obj.operation == "identity"
    assert filter_obj.args is not None
    assert isinstance(filter_obj.created_at, datetime)


def test_get_by_picker_id_returns_empty_if_none(db_session, filters_repo):
    # WHEN
    results = filters_repo.get_by_picker_id(9999)

    # THEN
    assert results == []


def test_get_by_picker_id_returns_none(db_session, filters_repo):
    # GIVEN
    db_session.execute(
        text(
            "INSERT INTO feeds (id, name)"
            "VALUES (1, 'feed_fake_name')"
        )
    )
    db_session.execute(
        text(
            "INSERT INTO sources (id, url)"
            "VALUES (1, 'www.fake_source.com/feed')"
        )
    )
    db_session.execute(
        text(
            "INSERT INTO pickers (source_id, feed_id, cronjob)"
            "VALUES (1, 1, 'teste')"
        )
    )
    db_session.execute(
        text("""
            INSERT INTO filters (picker_id, operation, args, created_at)
            VALUES (:picker_id, :operation, :args, :created_at)
        """),
        {
            "picker_id": 1,
            "operation": "identity",
            "args": "['x','y']",
            "created_at": datetime(2025, 1, 1, 12, 0, 0),
        }
    )
    db_session.commit()

    # WHEN
    results = filters_repo.get_by_picker_id(2)

    # THEN
    assert results == []
