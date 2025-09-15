from datetime import datetime
from uuid import UUID, uuid4

import psycopg
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.adapters.repositories.feeds_repository import FeedsRepository
from src.domain.models.feed import Feed, FeedRequest

TEST_DB_URL = "postgresql://postgres:postgres@localhost:5433/"
TEST_DB_NAME = "test_nebula_repo"


@pytest.fixture(scope="session")
def setup_test_db():
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
    engine = create_engine(setup_test_db)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS feeds CASCADE;"))
        conn.execute(text("""
            CREATE TABLE feeds (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                external_id UUID NOT NULL DEFAULT gen_random_uuid(),
                created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))

    session = testing_session_local()

    session.execute(text("TRUNCATE TABLE feeds RESTART IDENTITY CASCADE;"))
    session.commit()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def repo(db_session):
    return FeedsRepository(db_session)


def test_create_feed_successfully(repo, db_session):
    # GIVEN
    feed_request = FeedRequest(
        name="fake_feed_name"
    )

    # WHEN
    feed = repo.create(feed_request)

    # THEN
    assert feed is not None
    assert type(feed.id) is int
    assert feed.name == "fake_feed_name"
    assert type(feed.external_id) is UUID
    assert type(feed.created_at) is datetime


def test_get_all_feeds(repo, db_session):
    # GIVEN
    db_session.execute(
        text("""
            INSERT INTO feeds (name)
            VALUES (:name)
        """),
        {
            "name": "fake_feed_name",
        }
    )
    db_session.execute(
        text("""
            INSERT INTO feeds (name)
            VALUES (:name)
        """),
        {
            "name": "fake_feed_name_b",
        }
    )
    db_session.commit()

    # WHEN
    feeds = repo.get_all()

    # THEN
    assert len(feeds) == 2
    assert all(isinstance(feed, Feed) for feed in feeds)


def test_get_all_feeds_empty(repo, db_session):
    # WHEN
    feeds = repo.get_all()

    # THEN
    assert len(feeds) == 0


def test_get_by_external_id_returns_source(repo, db_session):
    # GIVEN
    external_id = str(uuid4())
    db_session.execute(
        text("""
            INSERT INTO feeds (external_id, name, created_at)
            VALUES (:external_id, :name, :created_at)
        """),
        {
            "external_id": external_id,
            "name": "Example",
            "created_at": datetime(2025, 1, 1, 12, 0, 0),
        }
    )
    db_session.commit()
    inserted_id = db_session.execute(text("SELECT id FROM feeds")).scalar_one()

    # WHEN
    feed = repo.get_by_external_id(UUID(external_id))

    # THEN
    assert feed is not None
    assert feed.id == inserted_id
    assert str(feed.external_id) == external_id
    assert feed.name == "Example"


def test_get_by_id_returns_source(repo, db_session):
    # GIVEN
    external_id = str(uuid4())
    feed_id = 99
    db_session.execute(
        text("""
            INSERT INTO feeds (id, external_id, name, created_at)
            VALUES (:feed_id, :external_id, :name, :created_at)
        """),
        {
            "feed_id": feed_id,
            "external_id": external_id,
            "name": "Example",
            "created_at": datetime(2025, 1, 1, 12, 0, 0),
        }
    )
    db_session.commit()
    inserted_id = db_session.execute(text("SELECT id FROM feeds")).scalar_one()

    # WHEN
    feed = repo.get_by_id(feed_id)

    # THEN
    assert feed is not None
    assert feed.id == inserted_id
    assert str(feed.external_id) == external_id
    assert feed.name == "Example"
