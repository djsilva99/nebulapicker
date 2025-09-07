import logging
import os
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from src.configs.dependencies.repositories import get_db
from src.main import app

TEST_DB_URL = "postgresql://postgres:postgres@localhost:5433/"
TEST_DB_NAME = "test_nebula"
TEST_DB_MIGRATIONS_DIR = str(
    Path(__file__).resolve().parents[2] / "infrastructure" / "db" / "alembic"
)
TEST_ALEMBIC_INI = str(Path(__file__).resolve().parents[2])


@pytest.fixture(scope="session")
def test_db_manager():
    """
    Manages the creation and dropping of the test database.
    This fixture ensures the database exists for the entire test session.
    """
    # Connect to the default postgres database to create/drop the test database
    with psycopg.connect(TEST_DB_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')
            cur.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')

    # Now run migrations on the newly created database
    test_db_url = f"{TEST_DB_URL}{TEST_DB_NAME}"
    alembic_cfg = Config(os.path.join(TEST_ALEMBIC_INI, "alembic.ini"))
    alembic_cfg.set_main_option("script_location", TEST_DB_MIGRATIONS_DIR)
    alembic_cfg.set_main_option("sqlalchemy.url", test_db_url)
    command.upgrade(alembic_cfg, "head")

    yield test_db_url

    # Teardown: Drop the test database after the session
    with psycopg.connect(TEST_DB_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')


@pytest.fixture(name="db_session")
def db_session_fixture(test_db_manager):
    """
    Provides a clean, transactional database session for each test.
    """
    engine = create_engine(test_db_manager)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    connection = engine.connect()
    transaction = connection.begin()
    session = testing_session_local(bind=connection)

    # Dependency override
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield session

    # Rollback the transaction to revert all changes
    transaction.rollback()
    connection.close()


@pytest.fixture(name="client")
def client_fixture(db_session: Session):
    """
    Fixture to create a test client for the application.
    """
    return TestClient(app)


def test_welcome(caplog):
    # WHEN
    client = TestClient(app)
    with caplog.at_level(logging.INFO):
        response = client.get("/v1")

    # THEN
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to NebulaPicker"}


def test_read_sources_empty(client: TestClient, db_session: Session):
    # WHEN
    response = client.get("/v1/sources/")

    # THEN
    assert response.status_code == 200
    assert response.json() == {'sources': []}


def test_read_sources_with_data(client: TestClient, db_session: Session):
    # GIVEN
    new_uuid = str(uuid4())
    db_session.execute(text(
        "INSERT INTO source (external_id, url, name) VALUES (:external_id, :url, :name);"
    ), {"external_id": new_uuid, "url": "https://example.com", "name": "Example Source"})
    db_session.commit()

    # WHEN
    response = client.get("/v1/sources/")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert len(data["sources"]) == 1
    assert data["sources"][0]["url"] == "https://example.com"
    assert data["sources"][0]["name"] == "Example Source"
    assert "external_id" in data["sources"][0]
