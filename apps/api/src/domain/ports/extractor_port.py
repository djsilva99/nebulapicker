from abc import ABC, abstractmethod

from src.domain.models.feed import (
    FeedItemContent,
    FeedItemImageUrl,
    GetFeedItemContentRequest,
    GetFeedItemImageUrlRequest,
)


class ExtractorPort(ABC):

    @abstractmethod
    def get_feed_item_content(
        self,
        get_feed_item_content_request: GetFeedItemContentRequest
    ) -> FeedItemContent | None:
        pass

    @abstractmethod
    def get_feed_item_image(
        self,
        get_feed_item_image_url_request: GetFeedItemImageUrlRequest
    ) -> FeedItemImageUrl | None:
        pass
