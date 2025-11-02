from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest
from src.domain.models.source import Source, SourceRequest
from src.domain.ports.sources_port import SourcePort
from src.domain.services.source_service import SourceService


@pytest.fixture
def mock_source_port():
    return Mock(spec=SourcePort)


@pytest.fixture
def source_service(mock_source_port):
    return SourceService(source_port=mock_source_port)


def test_get_all_sources_successfully(source_service, mock_source_port):
    # GIVEN
    fake_sources = [
        Source(
            id=1,
            external_id=uuid4(),
            url="https://example.com/1",
            name="Example 1",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
        ),
        Source(
            id=2,
            external_id=uuid4(),
            url="https://example.com/2",
            name="Example 2",
            created_at=datetime(2025, 1, 1, 12, 0, 0),
        ),
    ]
    mock_source_port.get_all_sources.return_value = fake_sources

    # WHEN
    result = source_service.get_all_sources()

    # THEN
    assert result == fake_sources
    mock_source_port.get_all_sources.assert_called_once()


def test_get_all_sources_that_returns_empty(source_service, mock_source_port):
    # GIVEN
    fake_sources = []
    mock_source_port.get_all_sources.return_value = fake_sources

    # WHEN
    result = source_service.get_all_sources()

    # THEN
    assert result == fake_sources
    mock_source_port.get_all_sources.assert_called_once()


def test_update_source_successfully(source_service, mock_source_port):
    # GIVEN
    source_external_id = uuid4()
    source_id = 123
    existing_source = Source(
        id=source_id,
        external_id=source_external_id,
        url="https://old.url.com",
        name="Old Name",
        created_at=datetime(2025, 1, 1, 12, 0, 0),
    )
    update_request = SourceRequest(url="https://new.url.com", name="New Name")
    updated_source = Source(
        id=source_id,
        external_id=source_external_id,
        url=update_request.url,
        name=update_request.name,
        created_at=existing_source.created_at,
    )
    mock_source_port.get_source_by_external_id.return_value = existing_source
    mock_source_port.update_source.return_value = updated_source

    # WHEN
    result = source_service.update_source(source_external_id, update_request)

    # THEN
    assert result == updated_source
    mock_source_port.get_source_by_external_id.assert_called_once_with(source_external_id)
    mock_source_port.update_source.assert_called_once_with(source_id, update_request)


def test_update_source_returns_none_when_source_not_found(source_service, mock_source_port):
    # GIVEN
    non_existent_external_id = uuid4()
    update_request = SourceRequest(url="https://any.url.com", name="Any Name")
    mock_source_port.get_source_by_external_id.return_value = None

    # WHEN
    result = source_service.update_source(non_existent_external_id, update_request)

    # THEN
    assert result is None
    mock_source_port.get_source_by_external_id.assert_called_once_with(non_existent_external_id)
    mock_source_port.update_source.assert_not_called()
