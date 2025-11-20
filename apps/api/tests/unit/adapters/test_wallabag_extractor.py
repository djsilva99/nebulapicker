from unittest.mock import MagicMock, patch

from src.adapters.wallabag_extractor import (
    MINIMUM_CONTENT_LEN,
    WallabagExtractor,
)
from src.domain.models.feed import FeedItemContent, GetFeedItemContentRequest


@patch("src.adapters.wallabag_extractor.requests.post")
@patch("src.adapters.wallabag_extractor.requests.delete")
def test_get_feed_item_content_success_long_content(mock_delete, mock_post):
    # GIVEN
    extractor = WallabagExtractor()
    token_response = MagicMock()
    token_response.json.return_value = {"access_token": "abc123"}
    token_response.raise_for_status.return_value = None
    long_content = "x" * (MINIMUM_CONTENT_LEN + 10)
    entry_response = MagicMock()
    entry_response.json.return_value = {
        "id": 42,
        "title": "Test Article",
        "content": long_content,
        "reading_time": 12,
    }
    mock_post.side_effect = [token_response, entry_response]
    request = GetFeedItemContentRequest(url="http://example.com/article")

    # WHEN
    result = extractor.get_feed_item_content(request)

    # THEN
    assert isinstance(result, FeedItemContent)
    assert result.title == "Test Article"
    assert result.content == long_content
    assert result.reading_time == 12
    mock_delete.assert_called_once()


@patch("src.adapters.wallabag_extractor.requests.post")
@patch("src.adapters.wallabag_extractor.requests.delete")
def test_get_feed_item_content_short_fallback(mock_delete, mock_post):
    # GIVEN
    extractor = WallabagExtractor()
    token_response = MagicMock()
    token_response.json.return_value = {"access_token": "abc123"}
    token_response.raise_for_status.return_value = None
    entry_response = MagicMock()
    entry_response.json.return_value = {
        "id": 100,
        "title": "Short Article",
        "content": "too short",
        "reading_time": 3,
    }
    mock_post.side_effect = [token_response, entry_response]
    request = GetFeedItemContentRequest(url="http://example.com/short")

    # WHEN
    result = extractor.get_feed_item_content(request)

    # THEN
    assert isinstance(result, FeedItemContent)
    assert result.title == "Short Article"
    assert result.content == "<p> Nebulapicker was not able to parse the content. </p>"
    assert result.reading_time == 0
    mock_delete.assert_called_once()


@patch("src.adapters.wallabag_extractor.requests.post")
def test_get_feed_item_content_exception_returns_none(mock_post):
    # GIVEN
    extractor = WallabagExtractor()
    mock_post.side_effect = Exception("Network error")
    request = GetFeedItemContentRequest(url="http://example.com/broken")

    # WHEN
    result = extractor.get_feed_item_content(request)

    # THEN
    assert result is None
