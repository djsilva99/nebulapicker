import logging
import os
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from src.adapters.scheduler import Scheduler
from src.configs.dependencies.repositories import get_db
from src.domain.services.job_service import JobService
from src.main import app

TEST_DB_URL = "postgresql://postgres:postgres@localhost:5433/"
TEST_DB_NAME = "test_nebula"
TEST_DB_MIGRATIONS_DIR = str(
    Path(__file__).resolve().parents[2] / "infrastructure" / "db" / "alembic"
)
TEST_ALEMBIC_INI = str(Path(__file__).resolve().parents[2])


@pytest.fixture
def mock_services():
    return {
        "scheduler": MagicMock(),
        "picker_service": MagicMock(),
        "filter_service": MagicMock(),
        "source_service": MagicMock(),
        "feed_service": MagicMock(),
        "extractor_service": MagicMock(),
    }


@pytest.fixture(autouse=True)
def setup_job_service(mock_services):
    scheduler = Scheduler()
    picker_service = mock_services["picker_service"]
    filter_service = mock_services["filter_service"]
    source_service = mock_services["source_service"]
    feed_service = mock_services["feed_service"]
    extractor_service = mock_services["extractor_service"]

    app.state.job_service = JobService(
        scheduler=scheduler,
        picker_service=picker_service,
        filter_service=filter_service,
        source_service=source_service,
        feed_service=feed_service,
        extractor_service=extractor_service
    )
    return


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
        response = client.get("/")

    # THEN
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Welcome to NebulaPicker"}


def test_read_sources_empty(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.get("/v1/sources", headers={"Authorization": f"Bearer {fake_token}"})

    # THEN
    assert response.status_code == 200
    assert response.json() == {'sources': []}


def test_read_sources_with_data(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    new_uuid = str(uuid4())
    db_session.execute(text(
        "INSERT INTO sources (external_id, url, name) VALUES (:external_id, :url, :name);"
    ), {"external_id": new_uuid, "url": "https://example.com", "name": "Example Source"})
    db_session.commit()
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.get("/v1/sources", headers={"Authorization": f"Bearer {fake_token}"})

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert len(data["sources"]) == 1
    assert data["sources"][0]["url"] == "https://example.com"
    assert data["sources"][0]["name"] == "Example Source"
    assert "external_id" in data["sources"][0]


def test_get_source_with_data(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    new_uuid = str(uuid4())
    db_session.execute(text(
        "INSERT INTO sources (external_id, url, name) VALUES (:external_id, :url, :name);"
    ), {"external_id": new_uuid, "url": "https://example.com", "name": "Example Source"})
    db_session.commit()
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.get(
        "/v1/sources/" + new_uuid, headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["url"] == "https://example.com"
    assert data["name"] == "Example Source"
    assert "external_id" in data


def test_get_source_without_data(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    new_uuid = str(uuid4())
    wrong_uuid = str(uuid4())
    db_session.execute(text(
        "INSERT INTO sources (external_id, url, name) VALUES (:external_id, :url, :name);"
    ), {"external_id": new_uuid, "url": "https://example.com", "name": "Example Source"})
    db_session.commit()
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.get(
        "/v1/sources/" + wrong_uuid, headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == 404


def test_update_source_successfully(
    client: TestClient,
    db_session: Session,
    mock_services,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    source_external_id = uuid4()
    db_session.execute(text(
        "INSERT INTO sources (external_id, url, name) VALUES (:external_id, :url, :name);"
    ), {"external_id": source_external_id, "url": "https://example.com", "name": "Example Source"})
    db_session.commit()
    update_payload = {
        "url": "https://new.updated.com/feed",
        "name": "New Source Name"
    }
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.put(
        f"/v1/sources/{source_external_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["external_id"] == str(source_external_id)
    assert response_data["url"] == update_payload["url"]
    assert response_data["name"] == update_payload["name"]


def test_update_source_not_found(
    client: TestClient,
    mock_services,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    non_existent_id = uuid4()
    update_payload = {
        "url": "https://some.url.com",
        "name": "Some Name"
    }
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.put(
        f"/v1/sources/{non_existent_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_source_successfully(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    source_external_id = uuid4()
    db_session.execute(text(
        "INSERT INTO sources (external_id, url, name) VALUES (:external_id, :url, :name);"
    ), {"external_id": source_external_id, "url": "https://example.com", "name": "Example Source"})
    db_session.commit()
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.delete(
        f"/v1/sources/{source_external_id}",
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == status.HTTP_204_NO_CONTENT



def test_delete_source_not_found(
    client: TestClient,
    mock_services,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    non_existent_id = uuid4()
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.delete(
        f"/v1/sources/{non_existent_id}",
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Source not found"


def test_list_feeds_empty(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch
):
    # WHEN
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)
    response = client.get(
        "/v1/feeds",
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == 200
    assert response.json() == {'feeds': []}


def test_list_feeds_with_data(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    new_uuid = str(uuid4())
    feed_id = 1
    feed_external_id = str(uuid4())
    db_session.execute(text(
        "INSERT INTO feeds (id, external_id, name) VALUES (1, :external_id, :name);"
    ), {"external_id": new_uuid, "name": "fake_name"})
    db_session.commit()
    db_session.execute(
        text(
            "INSERT INTO feed_items (feed_id, external_id, link, title, "
            "description, author) VALUES (:feed_id, :external_id, :link, "
            ":title, :description, :author);"
        ),
        {
            "external_id": feed_external_id,
            "feed_id": feed_id,
            "link": "fake_link",
            "title": "fake_title",
            "author": "fake_author",
            "description": "fake_description"
        }
    )
    db_session.commit()
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.get(
        "/v1/feeds",
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert len(data["feeds"]) == 1
    assert data["feeds"][0]["name"] == "fake_name"
    assert "external_id" in data["feeds"][0]


def test_create_feed_successfully(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    feed_payload = {
        "name": "fake_feed_name",
    }
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.post(
        "/v1/feeds/",
        json=feed_payload,
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == 201
    assert response.json()["name"] == "fake_feed_name"
    assert "external_id" in response.json()
    assert "created_at" in response.json()


def test_update_feed_successfully(
    client: TestClient,
    db_session: Session,
    mock_services,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    source_external_id = uuid4()
    db_session.execute(
        text(
            "INSERT INTO feeds (external_id, name) VALUES (:external_id, :name);"
        ),
        {"external_id": source_external_id, "name": "Example Feed"}
    )
    db_session.commit()
    update_payload = {
        "name": "New Feed Name"
    }
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.patch(
        f"/v1/feeds/{source_external_id}",
        json=update_payload,
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["external_id"] == str(source_external_id)
    assert response_data["name"] == update_payload["name"]


def test_delete_feed_successfully(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    feed_external_id = str(uuid4())
    db_session.execute(
        text("INSERT INTO feeds (id, external_id, name, created_at) "
             "VALUES (1, :external_id, 'feed_to_delete', NOW())"),
        {"external_id": feed_external_id}
    )
    db_session.execute(
        text("INSERT INTO sources (id, url, name) VALUES (1, 'https://example.com/src', 'src1')")
    )
    db_session.execute(
        text("INSERT INTO pickers (id, external_id, source_id, feed_id, cronjob, created_at) "
             "VALUES (1, :external_id, 1, 1, '*/5 * * * *', NOW())"),
        {"external_id": str(uuid4())}
    )
    db_session.execute(
        text("INSERT INTO filters (id, picker_id, operation, args, created_at) "
             "VALUES (1, 1, 'identity', '[a]', NOW()), (2, 1, 'identity', '[b]', NOW())")
    )
    db_session.execute(
        text("INSERT INTO feed_items (id, feed_id, title, link, description, author, created_at, "
             "is_active) "
             "VALUES (1, 1, 'feed_item_1', 'http://example.com/item1', "
             "'desc1', 'author1', NOW(), TRUE), "
             "(2, 1, 'feed_item_2', 'http://example.com/item2', 'desc2', 'author2', NOW(), TRUE)")
    )
    db_session.commit()
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.delete(
        f"/v1/feeds/{feed_external_id}",
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Ensure feed, pickers, filters, and feed_items are deleted
    remaining_feed = db_session.execute(
        text(
            "SELECT * FROM feeds WHERE id = 1"
        )
    ).first()
    remaining_picker = db_session.execute(
        text(
            "SELECT * FROM pickers WHERE feed_id = 1"
        )
    ).first()
    remaining_filters = db_session.execute(
        text(
            "SELECT * FROM filters WHERE picker_id = 1"
        )
    ).all()
    remaining_feed_items = db_session.execute(
        text(
            "SELECT * FROM feed_items WHERE feed_id = 1"
        )
    ).all()

    assert remaining_feed is None
    assert remaining_picker is None
    assert remaining_filters == []
    assert remaining_feed_items == []


def test_delete_feed_not_found(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    non_existent_id = uuid4()
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.delete(
        f"/v1/feeds/{non_existent_id}",
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Feed not found"


def test_create_picker_successfully(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    db_session.execute(
        text("INSERT INTO sources (id, url, name) VALUES (:id, :url, :name)"),
        {"id": 1, "url": "https://example.com/source", "name": "picker_source"}
    )
    db_session.commit()
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    picker_payload = {
        "source_url": "https://example.com/source",
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
    response = client.post(
        "/v1/pickers/",
        json=picker_payload,
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == 201
    data = response.json()
    assert data["source_url"] == "https://example.com/source"
    assert data["cronjob"] == "*/10 * * * *"
    assert "external_id" in data
    assert "created_at" in data


def test_create_picker_invalid_source_or_feed(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    picker_payload = {
        "source_url": 9999,
        "feed_external_id": 8888,
        "cronjob": "*/15 * * * *",
    }
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.post(
        "/v1/pickers/",
        json=picker_payload,
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == 400 or response.status_code == 422


def test_get_picker_successfully(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    db_session.execute(
        text("INSERT INTO sources (id, external_id, url, name) "
             "VALUES (:id, :external_id, :url, :name)"),
        {
            "id": 1,
            "external_id": str(uuid4()),
            "url": "https://example.com/source",
            "name": "picker_source"
        }
    )
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    feed_external_id = str(uuid4())
    db_session.execute(
        text("INSERT INTO feeds (id, external_id, name) "
             "VALUES (:id, :external_id, :name)"),
        {"id": 1, "external_id": feed_external_id, "name": "feed_name"}
    )

    picker_external_id = str(uuid4())
    db_session.execute(
        text("INSERT INTO pickers (id, external_id, source_id, feed_id, cronjob, created_at) "
             "VALUES (:id, :external_id, :source_id, :feed_id, :cronjob, NOW())"),
        {
            "id": 1,
            "external_id": picker_external_id,
            "source_id": 1,
            "feed_id": 1,
            "cronjob": "*/5 * * * *"
        }
    )

    db_session.execute(
        text("INSERT INTO filters (id, picker_id, operation, args, created_at) "
             "VALUES (:id, :picker_id, :operation, :args, NOW())"),
        {"id": 1, "picker_id": 1, "operation": "identity", "args": "[a]"}
    )
    db_session.commit()

    # WHEN
    response = client.get(
        f"/v1/pickers/{picker_external_id}",
        headers={"Authorization": f"Bearer {fake_token}"}
    )

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


def test_get_picker_not_found(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.get(
        f"/v1/pickers/{uuid4()}",
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == 404
    assert response.json()["detail"] == "Picker not found"


def test_delete_picker_successfully(
    client, db_session,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    db_session.execute(
        text("INSERT INTO sources (id, url, name) VALUES (1, 'https://example.com', 'src1');")
    )
    db_session.commit()

    feed_external_id = str(uuid4())
    db_session.execute(
        text("INSERT INTO feeds (id, external_id, name) VALUES (1, :external_id, 'feed1');"),
        {"external_id": feed_external_id},
    )
    db_session.commit()

    picker_external_id = str(uuid4())
    db_session.execute(
        text(
            "INSERT INTO pickers (id, external_id, source_id, feed_id, cronjob) "
            "VALUES (1, :external_id, 1, 1, '*/5 * * * *');"
        ),
        {"external_id": picker_external_id},
    )
    db_session.commit()

    db_session.execute(
        text(
            "INSERT INTO filters (id, picker_id, operation, args) "
            "VALUES (1, 1, 'identity', '[a]'), (2, 1, 'identity', '[b]');"
        )
    )
    db_session.commit()

    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.delete(
        f"/v1/pickers/{picker_external_id}",
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == status.HTTP_204_NO_CONTENT
    picker = db_session.execute(text("SELECT * FROM pickers WHERE id = 1")).first()
    assert picker is None
    filters = db_session.execute(text("SELECT * FROM filters WHERE picker_id = 1")).all()
    assert filters == []


def test_delete_picker_not_found(
    client,
    db_session,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    missing_external_id = str(uuid4())
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.delete(
        f"/v1/pickers/{missing_external_id}",
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Picker not found"}


def test_get_feed_rss_successfully(client: TestClient, db_session: Session):
    # GIVEN
    feed_external_id = str(uuid4())
    db_session.execute(
        text("INSERT INTO feeds (id, external_id, name, created_at) "
             "VALUES (1, :external_id, 'rss_feed', NOW())"),
        {"external_id": feed_external_id}
    )
    db_session.execute(
        text("INSERT INTO feed_items (id, feed_id, title, link, description, author, created_at) "
             "VALUES (1, 1, 'item_title', 'http://example.com/item1', "
             "'item_description', 'test_author', NOW())")
    )
    db_session.commit()

    # WHEN
    response = client.get(f"/v1/feeds/{feed_external_id}.xml")

    # THEN
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/rss+xml")
    assert f"{feed_external_id}.xml" in response.headers["content-disposition"]
    assert "<rss" in response.text
    assert "<title>item_title</title>" in response.text


def test_get_feed_successfully(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch
):
    # GIVEN
    db_session.execute(
        text("INSERT INTO sources (id, external_id, url, name) "
             "VALUES (1, :external_id, 'https://example.com/source', 'src1')"),
        {"external_id": str(uuid4())}
    )
    feed_external_id = str(uuid4())
    db_session.execute(
        text("INSERT INTO feeds (id, external_id, name, created_at) "
             "VALUES (1, :external_id, 'feed1', NOW())"),
        {"external_id": feed_external_id}
    )
    picker_external_id = str(uuid4())
    db_session.execute(
        text("INSERT INTO pickers (id, external_id, source_id, feed_id, cronjob, created_at) "
             "VALUES (1, :external_id, 1, 1, '*/5 * * * *', NOW())"),
        {"external_id": picker_external_id}
    )
    db_session.execute(
        text("INSERT INTO filters (id, picker_id, operation, args, created_at) "
             "VALUES (1, 1, 'identity', '[a]', NOW())")
    )
    db_session.execute(
        text("INSERT INTO feed_items (id, feed_id, title, link, description, author, "
             "content, reading_time, created_at) "
             "VALUES (1, 1, 'feed_item_title', 'http://example.com/item1', "
             "'feed_item_description', 'author_test', 'test_content', 2, NOW())")
    )
    db_session.commit()
    fake_token = "test-token"
    monkeypatch.setattr("src.adapters.entrypoints.v1.routes.generated_token", fake_token)

    # WHEN
    response = client.get(
        f"/v1/feeds/{feed_external_id}",
        headers={"Authorization": f"Bearer {fake_token}"}
    )

    # THEN
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "feed1"
    assert data["external_id"] == feed_external_id
    assert "created_at" in data
    assert len(data["pickers"]) == 1
    picker = data["pickers"][0]
    assert picker["cronjob"] == "*/5 * * * *"
    assert picker["source_url"] == "https://example.com/source"
    assert picker["external_id"] == picker_external_id
    assert isinstance(picker["filters"], list)
    assert picker["filters"][0]["operation"] == "identity"
    assert picker["filters"][0]["args"] == "[a]"
    assert len(data["feed_items"]) == 1
    assert data["feed_items"][0]["title"] == "feed_item_title"
    assert data["feed_items"][0]["link"] == "http://example.com/item1"
