import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, patch
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
from src.domain.models.job import JobRequest
from src.main import app

TEST_DB_URL = "postgresql://postgres:postgres@localhost:5433/"
TEST_DB_NAME = "test_nebula"
TEST_DB_MIGRATIONS_DIR = str(
    Path(__file__).resolve().parents[2] / "infrastructure" / "db" / "alembic"
)
TEST_ALEMBIC_INI = str(Path(__file__).resolve().parents[2])


@pytest.fixture(scope="session")
def test_db_manager():
    with psycopg.connect(TEST_DB_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')
            cur.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')

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

    transaction.rollback()
    connection.close()


@pytest.fixture(name="client")
def client_fixture(db_session: Session):
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
        "INSERT INTO sources (external_id, url, name) VALUES (:external_id, :url, :name);"
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


def test_add_cronjob_success(db_session: Session):
    # GIVEN
    job_payload = {
        "func_name": "process_feed",
        "schedule": "*/5 * * * *",
        "args": ["https://example.com/feed.xml"],
    }

    mock_job_service = MagicMock()

    # WHEN
    with patch("src.main.JobService", return_value=mock_job_service):
        with TestClient(app) as client:
            response = client.post("/v1/job/", json=job_payload)

    # THEN
    assert response.status_code == 201
    assert response.json() == {'msg': 'Job created'}

    expected_job_request = JobRequest(
        func_name="process_feed",
        schedule="*/5 * * * *",
        args=["https://example.com/feed.xml"],
    )

    mock_job_service.add_cronjob.assert_called_once_with(expected_job_request)


def test_list_feeds_empty(client: TestClient, db_session: Session):
    # WHEN
    response = client.get("/v1/feeds/")

    # THEN
    assert response.status_code == 200
    assert response.json() == {'feeds': []}


def test_list_feeds_with_data(client: TestClient, db_session: Session):
    # GIVEN
    new_uuid = str(uuid4())
    db_session.execute(text(
        "INSERT INTO feeds (external_id, name) VALUES (:external_id, :name);"
    ), {"external_id": new_uuid, "name": "fake_name"})
    db_session.commit()

    # WHEN
    response = client.get("/v1/feeds/")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert len(data["feeds"]) == 1
    assert data["feeds"][0]["name"] == "fake_name"
    assert "external_id" in data["feeds"][0]


def test_create_feed(client: TestClient, db_session: Session):
    # GIVEN
    feed_payload = {
        "name": "fake_feed_name",
    }

    # WHEN
    response = client.post("/v1/feeds/", json=feed_payload)

    # THEN
    assert response.status_code == 201
    assert response.json()["name"] == "fake_feed_name"
    assert "external_id" in response.json()
    assert "created_at" in response.json()


def test_create_picker_success(client: TestClient, db_session: Session):
    # GIVEN
    db_session.execute(
        text("INSERT INTO sources (id, url, name) VALUES (:id, :url, :name)"),
        {"id": 1, "url": "https://example.com/source", "name": "picker_source"}
    )
    db_session.commit()

    picker_payload = {
        "source_url": "https://example.com/source",
        #"feed_id": feed_id,
        "cronjob": "*/10 * * * *",
        "filters": [
            {
                "operation": "identity",
                "args": "[a]"
            },
            {
                "operation": "identity",
                "args": "[b]"
            }
        ]
    }

    # WHEN
    response = client.post("/v1/pickers/", json=picker_payload)

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["source_url"] == "https://example.com/source"
    assert data["cronjob"] == "*/10 * * * *"
    assert "external_id" in data
    assert "created_at" in data


def test_create_picker_invalid_source_or_feed(client: TestClient, db_session: Session):
    # GIVEN
    picker_payload = {
        "source_url": 9999,
        "feed_external_id": 8888,
        "cronjob": "*/15 * * * *",
    }

    # WHEN
    response = client.post("/v1/pickers/", json=picker_payload)

    # THEN
    assert response.status_code == 400 or response.status_code == 422


def test_get_picker_success(client: TestClient, db_session: Session):
    # GIVEN: create source
    db_session.execute(
        text("INSERT INTO sources (id, external_id, url, name) "
             "VALUES (:id, :external_id, :url, :name)"),
        {"id": 1, "external_id": str(uuid4()), "url": "https://example.com/source", "name": "picker_source"}
    )

    # GIVEN: create feed
    feed_external_id = str(uuid4())
    db_session.execute(
        text("INSERT INTO feeds (id, external_id, name) "
             "VALUES (:id, :external_id, :name)"),
        {"id": 1, "external_id": feed_external_id, "name": "feed_name"}
    )

    # GIVEN: create picker
    picker_external_id = str(uuid4())
    db_session.execute(
        text("INSERT INTO pickers (id, external_id, source_id, feed_id, cronjob, created_at) "
             "VALUES (:id, :external_id, :source_id, :feed_id, :cronjob, NOW())"),
        {"id": 1, "external_id": picker_external_id, "source_id": 1, "feed_id": 1, "cronjob": "*/5 * * * *"}
    )

    # GIVEN: create filters
    db_session.execute(
        text("INSERT INTO filters (id, picker_id, operation, args, created_at) "
             "VALUES (:id, :picker_id, :operation, :args, NOW())"),
        {"id": 1, "picker_id": 1, "operation": "identity", "args": "[a]"}
    )
    db_session.commit()

    # WHEN
    response = client.get(f"/v1/pickers/{picker_external_id}")

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["external_id"] == picker_external_id
    assert data["source_url"] == "https://example.com/source"
    assert data["feed_external_id"] == feed_external_id
    assert data["cronjob"] == "*/5 * * * *"
    assert isinstance(data["filters"], list)
    assert len(data["filters"]) == 1
    assert data["filters"][0]["operation"] == "identity"
    assert data["filters"][0]["args"] == "[a]"


def test_get_picker_not_found(client: TestClient):
    # WHEN
    response = client.get(f"/v1/pickers/{uuid4()}")

    # THEN
    assert response.status_code == 404
    assert response.json()["detail"] == "Picker not found"
