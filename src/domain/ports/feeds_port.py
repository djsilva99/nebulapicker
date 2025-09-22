from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.models.feed import Feed, FeedItem, FeedItemRequest, FeedRequest


class FeedsPort(ABC):

    @abstractmethod
    def create_feed(self, feed_request: FeedRequest) -> Feed:
        pass

    @abstractmethod
    def get_all_feeds(self) -> list[Feed]:
        pass

    @abstractmethod
    def get_feed_by_external_id(self, external_id: UUID) -> Feed | None:
        pass

    @abstractmethod
    def get_feed_by_id(self, id: int) -> Feed | None:
        pass

    @abstractmethod
    def get_feed_items_by_feed_id(self, feed_id: int) -> list[FeedItem]:
        pass

    @abstractmethod
    def create_feed_item(self, feed_item_request: FeedItemRequest) -> FeedItem:
        pass
