from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest
from src.domain.models.source import Source
from src.domain.ports.sources_port import SourcePort
from src.domain.services.source_service import SourceService


@pytest.fixture
def mock_source_port():
    return Mock(spec=SourcePort)


@pytest.fixture
def source_service(mock_source_port):
    return SourceService(source_port=mock_source_port)


def test_get_all_sources_returns_sources(source_service, mock_source_port):
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


def test_get_all_sources_returns_empty(source_service, mock_source_port):
    # GIVEN
    fake_sources = []
    mock_source_port.get_all_sources.return_value = fake_sources

    # WHEN
    result = source_service.get_all_sources()

    # THEN
    assert result == fake_sources
    mock_source_port.get_all_sources.assert_called_once()
