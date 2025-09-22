from datetime import datetime
from uuid import uuid4

import psycopg
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.adapters.repositories.pickers_repository import PickersRepository
from src.domain.models.picker import Picker, PickerRequest

TEST_DB_URL = "postgresql://postgres:postgres@localhost:5433/"
TEST_DB_NAME = "test_nebula_repo"


@pytest.fixture(scope="session")
def setup_test_db():
    with psycopg.connect(TEST_DB_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')
            cur.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')

    test_db_url = f"{TEST_DB_URL}{TEST_DB_NAME}"

    # Setup schema once
    engine = create_engine(test_db_url)
    with engine.begin() as conn:
        conn.execute(text("""
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
        """))

    yield test_db_url

    # Drop the test database after the session
    with psycopg.connect(TEST_DB_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')


@pytest.fixture
def db_session(setup_test_db):
    engine = create_engine(setup_test_db)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = testing_session_local()

    # Truncate all tables to reset state
    session.execute(text("TRUNCATE TABLE pickers, feeds, sources RESTART IDENTITY CASCADE;"))
    session.commit()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def pickers_repo(db_session):
    return PickersRepository(db_session)



def test_create_picker_successfully(db_session, pickers_repo):
    # GIVEN
    picker_request = PickerRequest(
        feed_id=1,
        source_id=1,
        cronjob="1,31 * * * *"
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
    db_session.commit()

    # WHEN
    created = pickers_repo.create_picker(picker_request)

    # THEN
    assert created.source_id == 1
    assert created.feed_id == 1
    assert created.cronjob == "1,31 * * * *"
    assert isinstance(created.created_at, datetime)
    row = db_session.execute(
        text(
            "SELECT * FROM pickers WHERE id = :id"
        ),
        {
            "id": created.id
        }
    ).first()
    assert row is not None


def test_get_picker_by_external_id_success(db_session, pickers_repo):
    # GIVEN
    external_id = uuid4()
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
        text("""
            INSERT INTO pickers (id, feed_id, source_id, cronjob, external_id, created_at)
            VALUES (:id, :feed_id, :source_id, :cronjob, :external_id, :created_at)
        """),
        {
            "id": 1,
            "feed_id": 1,
            "source_id": 1,
            "cronjob": "* * * * *",
            "external_id": str(external_id),
            "created_at": datetime(2025, 1, 1, 12, 0, 0),
        }
    )
    db_session.commit()

    # WHEN
    result = pickers_repo.get_picker_by_external_id(external_id)

    # THEN
    assert result is not None
    assert result.id == 1
    assert result.feed_id == 1
    assert result.source_id == 1
    assert result.cronjob == "* * * * *"
    assert result.external_id == external_id


def test_get_picker_by_external_id_returns_none(db_session, pickers_repo):
    # WHEN
    results = pickers_repo.get_picker_by_external_id(uuid4())

    # THEN
    assert results is None


def test_delete_picker_for_existing_picker(db_session):
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
    db_session.execute(text(
        "INSERT INTO pickers (source_id, feed_id, cronjob, external_id) "
        "VALUES (:source_id, :feed_id, :cronjob, gen_random_uuid())"
    ), {"source_id": 1, "feed_id": 1, "cronjob": "*/5 * * * *"})
    db_session.commit()

    picker_id = db_session.execute(text("SELECT id FROM pickers LIMIT 1")).scalar_one()

    repo = PickersRepository(db_session)

    # WHEN
    deleted = repo.delete_picker(picker_id)

    # THEN
    assert deleted is True
    result = db_session.execute(
        text("SELECT * FROM pickers WHERE id = :id"),
        {"id": picker_id}
    ).first()
    assert result is None


def test_delete_picker_for_non_existing_picker(db_session):
    repo = PickersRepository(db_session)

    # WHEN
    deleted = repo.delete_picker(99999)

    # THEN
    assert deleted is False


def test_get_pickers_by_feed_id_successfully(pickers_repo, db_session):
    # GIVEN
    now = datetime(2025, 1, 1, 12, 0, 0)
    feed_id = db_session.execute(
        text("""
            INSERT INTO feeds (
                name,
                external_id,
                created_at
            )
            VALUES (
                :name,
                :external_id,
                :created_at
            )
            RETURNING id
        """),
        {
            "name": "Test Feed",
            "external_id": uuid4(),
            "created_at": now,
        },
    ).scalar_one()

    other_feed_id = db_session.execute(
        text("""
            INSERT INTO feeds (
                name,
                external_id,
                created_at
            )
            VALUES (
                :name,
                :external_id,
                :created_at
            )
            RETURNING id
        """),
        {
            "name": "Other Feed",
            "external_id": uuid4(),
            "created_at": now,
        },
    ).scalar_one()

    source_id1 = db_session.execute(
        text("""
            INSERT INTO sources (
                name,
                external_id,
                url,
                created_at
            )
            VALUES (
                :name,
                :external_id,
                :url,
                :created_at
            )
            RETURNING id
        """),
        {
            "name": "Source A",
            "external_id": uuid4(),
            "url": "www.example2.com/feed",
            "created_at": now,
        },
    ).scalar_one()

    source_id2 = db_session.execute(
        text("""
            INSERT INTO sources (
                name,
                external_id,
                url,
                created_at
            )
            VALUES (
                :name,
                :external_id,
                :url,
                :created_at
            )
            RETURNING id
        """),
        {
            "name": "Source B",
            "external_id": uuid4(),
            "url": "www.example.com/feed",
            "created_at": now,
        },
    ).scalar_one()

    db_session.execute(
        text("""
            INSERT INTO pickers (id, external_id, source_id, feed_id, cronjob, created_at)
            VALUES
                (1, :ext1, :source1, :feed_id, '0 * * * *', :created_at),
                (2, :ext2, :source2, :feed_id, '30 * * * *', :created_at),
                (3, :ext3, :source3, :other_feed_id, '15 * * * *', :created_at)
        """),
        {
            "ext1": uuid4(),
            "ext2": uuid4(),
            "ext3": uuid4(),
            "source1": source_id1,
            "source2": source_id2,
            "source3": source_id1,
            "feed_id": feed_id,
            "other_feed_id": other_feed_id,
            "created_at": now,
        },
    )
    db_session.commit()

    # WHEN
    pickers = pickers_repo.get_pickers_by_feed_id(feed_id)

    # THEN
    assert len(pickers) == 2
    assert all(isinstance(p, Picker) for p in pickers)
    assert all(p.feed_id == feed_id for p in pickers)
    cronjobs = [p.cronjob for p in pickers]
    assert "0 * * * *" in cronjobs
    assert "30 * * * *" in cronjobs


def test_get_picker_by_id_that_returns_picker(pickers_repo, db_session):
    # GIVEN
    now = datetime(2025, 1, 1, 12, 0, 0)
    db_session.execute(text("INSERT INTO feeds (id, name) VALUES (1, 'Feed A')"))
    db_session.execute(text("INSERT INTO sources (id, url) VALUES (1, 'https://example.com/feed')"))
    db_session.execute(
        text("""
            INSERT INTO pickers (id, external_id, source_id, feed_id, cronjob, created_at)
            VALUES (:id, :external_id, :source_id, :feed_id, :cronjob, :created_at)
        """),
        {
            "id": 1,
            "external_id": str(uuid4()),
            "source_id": 1,
            "feed_id": 1,
            "cronjob": "0 * * * *",
            "created_at": now,
        },
    )
    db_session.commit()

    # WHEN
    picker = pickers_repo.get_picker_by_id(1)

    # THEN
    assert picker is not None
    assert isinstance(picker, Picker)
    assert picker.id == 1
    assert picker.feed_id == 1
    assert picker.source_id == 1
    assert picker.cronjob == "0 * * * *"
    assert picker.created_at == now


def test_get_picker_by_id_that_returns_none_if_not_found(pickers_repo):
    # WHEN
    picker = pickers_repo.get_picker_by_id(999)

    # THEN
    assert picker is None


def test_get_all_pickers_that_returns_multiple(pickers_repo, db_session):
    # GIVEN
    now = datetime(2025, 1, 1, 12, 0, 0)
    db_session.execute(text("INSERT INTO feeds (id, name) VALUES (1, 'Feed A'), (2, 'Feed B')"))
    db_session.execute(
        text(
            "INSERT INTO sources (id, url) VALUES (1, 'https://example.com/a'), "
            "(2, 'https://example.com/b')"
        )
    )
    db_session.execute(
        text("""
            INSERT INTO pickers (id, external_id, source_id, feed_id, cronjob, created_at)
            VALUES
                (1, :ext1, 1, 1, '0 * * * *', :created_at),
                (2, :ext2, 2, 2, '30 * * * *', :created_at)
        """),
        {
            "ext1": uuid4(),
            "ext2": uuid4(),
            "created_at": now,
        },
    )
    db_session.commit()

    # WHEN
    pickers = pickers_repo.get_all_pickers()

    # THEN
    assert isinstance(pickers, list)
    assert len(pickers) == 2
    assert all(isinstance(p, Picker) for p in pickers)
    assert {p.id for p in pickers} == {1, 2}
    assert {p.cronjob for p in pickers} == {"0 * * * *", "30 * * * *"}


def test_get_all_pickers_that_returns_empty_list(pickers_repo):
    # WHEN
    pickers = pickers_repo.get_all_pickers()

    # THEN
    assert isinstance(pickers, list)
    assert pickers == []
