from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from src.domain.models.feed import Feed, FeedRequest
from src.domain.services.feed_service import FeedService


@pytest.fixture
def scheduler_mock():
    return MagicMock()


@pytest.fixture
def feeds_port_mock():
    return MagicMock()


@pytest.fixture
def feed_service(feeds_port_mock):
    return FeedService(feeds_port=feeds_port_mock)


def test_create_feed_ports(feed_service, feeds_port_mock):
    # GIVEN
    feed_request = FeedRequest(
        name="fake_name"
    )

    # WHEN
    feed_service.create_feed(feed_request)

    # THEN
    feeds_port_mock.create.assert_called_once_with(feed_request)


def test_get_all_feeds(feed_service, feeds_port_mock):
    # GIVEN
    feeds = [
        Feed(
            id=1,
            name="feed_name_1",
            external_id=uuid4(),
            created_at=datetime(2025, 1, 1, 12, 0, 0)
        ),
        Feed(
            id=3,
            name="feed_name_3",
            external_id=uuid4(),
            created_at=datetime(2025, 1, 1, 14, 0, 0)
        ),
    ]
    feeds_port_mock.get_all.return_value = feeds

    # WHEN
    all_feeds = feed_service.get_all_feeds()

    # THEN
    feeds_port_mock.get_all.assert_called_once()
    assert all_feeds == feeds
