from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from src.domain.models.feed import Feed, FeedItem, FeedRequest, UpdateFeedRequest
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


def test_create_feed(feed_service, feeds_port_mock):
    # GIVEN
    feed_request = FeedRequest(
        name="fake_name"
    )

    # WHEN
    feed_service.create_feed(feed_request)

    # THEN
    feeds_port_mock.create_feed.assert_called_once_with(feed_request)


def test_update_feed_successfully(feed_service, feeds_port_mock):
    # GIVEN
    feed_external_id = uuid4()
    feed_id = 123
    existing_feed = Feed(
        id=feed_id,
        external_id=feed_external_id,
        name="Old Name",
        created_at=datetime(2025, 1, 1, 12, 0, 0),
    )
    updated_feed = Feed(
        id=feed_id,
        external_id=feed_external_id,
        name="Updated name",
        created_at=datetime(2025, 1, 1, 12, 0, 0),
    )
    feeds_port_mock.get_feed_by_external_id.return_value = existing_feed
    feeds_port_mock.update_feed.return_value = updated_feed
    update_request = UpdateFeedRequest(name="Updated name")

    # WHEN
    result = feed_service.update_feed(feed_external_id, update_request)

    # THEN
    assert result == updated_feed
    feeds_port_mock.update_feed.assert_called_once_with(
        feed_id,
        update_request
    )


def test_update_feed_when_feed_does_not_exist(feed_service, feeds_port_mock):
    # GIVEN
    feed_external_id = uuid4()
    feeds_port_mock.get_feed_by_external_id.return_value = None
    update_request = UpdateFeedRequest(name="Updated name")

    # WHEN
    result = feed_service.update_feed(feed_external_id, update_request)

    # THEN
    assert result is None


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
    feeds_port_mock.get_all_feeds.return_value = feeds

    # WHEN
    all_feeds = feed_service.get_all_feeds()

    # THEN
    feeds_port_mock.get_all_feeds.assert_called_once()
    assert all_feeds == feeds


def test_get_feed_items_delegates_to_port(feed_service, feeds_port_mock):
    # GIVEN
    item1 = MagicMock(
        spec=FeedItem, created_at=datetime(2025, 1, 1, 14, 0, 0)
    )
    item2 = MagicMock(
        spec=FeedItem, created_at=datetime(2025, 1, 1, 12, 0, 0)
    )
    expected_items_sorted = [item2, item1]
    feeds_port_mock.get_feed_items_by_feed_id.return_value = [item1, item2]

    # WHEN
    result = feed_service.get_feed_items(feed_id=42)

    # THEN
    feeds_port_mock.get_feed_items_by_feed_id.assert_called_once_with(42)
    assert result == expected_items_sorted


def test_get_rss_builds_rss_feed(feed_service, feeds_port_mock):
    # GIVEN
    feed = Feed(
        id=1,
        name="Example Feed",
        external_id=uuid4(),
        created_at=datetime(2025, 1, 1, 12, 0, 0),
    )
    items = [
        FeedItem(
            id=10,
            feed_id=feed.id,
            external_id=uuid4(),
            link="https://example.com/1",
            title="First item",
            description="Desc 1",
            created_at=datetime(2025, 1, 2, 12, 0, 0),
        ),
        FeedItem(
            id=11,
            feed_id=feed.id,
            external_id=uuid4(),
            link="https://example.com/2",
            title="Second item",
            description="Desc 2",
            created_at=datetime(2025, 1, 3, 12, 0, 0),
        ),
    ]
    feeds_port_mock.get_feed_by_external_id.return_value = feed
    feeds_port_mock.get_feed_items_by_feed_id.return_value = items

    # WHEN
    rss_xml = feed_service.get_rss(feed.external_id)

    # THEN
    assert "<rss" in rss_xml
    assert "<title>Example Feed</title>" in rss_xml
    assert "https://example.com/1" in rss_xml
    assert "First item" in rss_xml
    assert "Second item" in rss_xml
    assert "<description>Desc 2</description>" in rss_xml

    feeds_port_mock.get_feed_by_external_id.assert_called_once_with(feed.external_id)
    feeds_port_mock.get_feed_items_by_feed_id.assert_called_once_with(feed.id)


def test_get_feed_by_external_id_delegates_to_port(feed_service, feeds_port_mock):
    # GIVEN
    external_id = uuid4()
    feed = Feed(
        id=99,
        name="Delegated Feed",
        external_id=external_id,
        created_at=datetime(2025, 2, 1, 12, 0, 0),
    )
    feeds_port_mock.get_feed_by_external_id.return_value = feed

    # WHEN
    result = feed_service.get_feed_by_external_id(external_id)

    # THEN
    feeds_port_mock.get_feed_by_external_id.assert_called_once_with(external_id)
    assert result == feed


def test_create_feed_item_delegates_to_port(feed_service, feeds_port_mock):
    # GIVEN
    feed_item_request = MagicMock()
    expected_feed_item = MagicMock(spec=FeedItem)
    feeds_port_mock.create_feed_item.return_value = expected_feed_item

    # WHEN
    result = feed_service.create_feed_item(feed_item_request)

    # THEN
    feeds_port_mock.create_feed_item.assert_called_once_with(feed_item_request)
    assert result == expected_feed_item
