from abc import ABC, abstractmethod

from src.domain.models.feed import FeedItemContent, GetFeedItemContentRequest


class ExtractorPort(ABC):

    @abstractmethod
    def get_feed_item_content(
        self,
        get_feed_item_content_request: GetFeedItemContentRequest
    ) -> FeedItemContent | None:
        pass
