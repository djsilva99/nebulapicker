from datetime import datetime
from uuid import UUID, uuid4

import psycopg
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.adapters.repositories.sources_repository import SourcesRepository
from src.domain.models.source import Source, SourceRequest

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

    session.execute(text("TRUNCATE TABLE sources RESTART IDENTITY CASCADE;"))
    session.commit()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def repo(db_session):
    return SourcesRepository(db_session)


def test_get_sourcce_by_external_successfully(repo, db_session):
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
    source = repo.get_source_by_external_id(UUID(external_id))

    # THEN
    assert source is not None
    assert source.id == inserted_id
    assert str(source.external_id) == external_id
    assert source.url == "https://example.com"
    assert source.name == "Example"


def test_get_source_by_id_successfully(repo, db_session):
    # GIVEN
    source_id = 1
    external_id = str(uuid4())
    db_session.execute(
        text("""
            INSERT INTO sources (id, external_id, url, name, created_at)
            VALUES (:source_id, :external_id, :url, :name, :created_at)
        """),
        {
            "source_id": source_id,
            "external_id": external_id,
            "url": "https://example.com",
            "name": "Example",
            "created_at": datetime(2025, 1, 1, 12, 0, 0),
        }
    )
    db_session.commit()
    inserted_id = db_session.execute(text("SELECT id FROM sources")).scalar_one()

    # WHEN
    source = repo.get_source_by_id(source_id)

    # THEN
    assert source is not None
    assert source.id == inserted_id
    assert source.url == "https://example.com"
    assert source.name == "Example"


def test_get_source_by_url_successfully(repo, db_session):
    # GIVEN
    url = "www.test.com/feed"
    external_id = str(uuid4())
    db_session.execute(
        text("""
            INSERT INTO sources (external_id, url, name, created_at)
            VALUES (:external_id, :url, :name, :created_at)
        """),
        {
            "external_id": external_id,
            "url": url,
            "name": "Example",
            "created_at": datetime(2025, 1, 1, 12, 0, 0),
        }
    )
    db_session.commit()
    inserted_id = db_session.execute(text("SELECT id FROM sources")).scalar_one()

    # WHEN
    source = repo.get_source_by_url(url)

    # THEN
    assert source is not None
    assert source.id == inserted_id
    assert str(source.external_id) == external_id
    assert source.url == url
    assert source.name == "Example"


def test_get_all_sources_successfully(repo, db_session):
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
    sources = repo.get_all_sources()

    # THEN
    assert len(sources) == 2
    assert all(isinstance(s, Source) for s in sources)


def test_get_all_sources_that_returns_empty(repo, db_session):
    # WHEN
    sources = repo.get_all_sources()

    # THEN
    assert len(sources) == 0


def test_get_source_by_external_id_that_returns_none_when_not_found(repo, db_session):
    # WHEN
    source = repo.get_source_by_external_id(uuid4())

    # THEN
    assert source is None


def test_get_source_by_url_returns_none_when_not_found(repo, db_session):
    # WHEN
    source = repo.get_source_by_url("www.test.com/feed")

    # THEN
    assert source is None


def test_update_source_successfully(repo, db_session):
    # GIVEN
    initial_external_id = str(uuid4())
    initial_url = "https://old.url.com"
    initial_name = "Old Name"
    initial_created_at = datetime(2025, 5, 1, 10, 0, 0)
    db_session.execute(
        text("""
            INSERT INTO sources (external_id, url, name, created_at)
            VALUES (:external_id, :url, :name, :created_at)
            RETURNING id
        """),
        {
            "external_id": initial_external_id,
            "url": initial_url,
            "name": initial_name,
            "created_at": initial_created_at,
        }
    )
    db_session.commit()
    inserted_source = db_session.execute(
        text("SELECT id, external_id, created_at FROM sources WHERE url = :url"),
        {"url": initial_url}
    ).mappings().first()
    source_id_to_update = inserted_source["id"]
    new_url = "https://new.updated.url/feed"
    new_name = "New Updated Name"
    source_request = SourceRequest(url=new_url, name=new_name)

    # WHEN
    updated_source = repo.update_source(source_id_to_update, source_request)

    # THEN
    assert updated_source is not None
    assert updated_source.id == source_id_to_update
    assert str(updated_source.external_id) == initial_external_id
    assert updated_source.url == new_url
    assert updated_source.name == new_name


def test_delete_source_successfully(repo, db_session):
    # GIVEN
    db_session.execute(
        text("""
            INSERT INTO sources (external_id, url, name)
            VALUES (:external_id, :url, :name)
        """),
        {
            "external_id": str(uuid4()),
            "url": "https://delete-me.com",
            "name": "To Delete"
        }
    )
    db_session.commit()
    source_id_to_delete = db_session.execute(
        text("SELECT id FROM sources WHERE url = 'https://delete-me.com'")
    ).scalar_one()

    # WHEN
    result = repo.delete_source(source_id_to_delete)

    # THEN
    assert result is True
    remaining_source = db_session.execute(
        text("SELECT * FROM sources WHERE id = :id"),
        {"id": source_id_to_delete}
    ).first()
    assert remaining_source is None


def test_delete_source_returns_false_when_not_found(repo, db_session):
    # GIVEN
    non_existent_id = 99999

    # WHEN
    result = repo.delete_source(non_existent_id)

    # THEN
    assert result is False
    count = db_session.execute(text("SELECT COUNT(*) FROM sources")).scalar_one()
    assert count == 0
