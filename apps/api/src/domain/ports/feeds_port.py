from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.domain.models.feed import (
    Feed,
    FeedItem,
    FeedItemRequest,
    FeedRequest,
    UpdateFeedItemRequest,
    UpdateFeedItemsRequest,
    UpdateFeedRequest,
)


class FeedsPort(ABC):

    @abstractmethod
    def create_feed(self, feed_request: FeedRequest) -> Feed:
        pass

    @abstractmethod
    def update_feed(
        self,
        feed_external_id: int,
        update_feed_request: UpdateFeedRequest
    ) -> Feed:
        pass

    @abstractmethod
    def delete_feed(self, feed_id: int) -> bool:
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
    def get_all_feed_items_by_feed_id(self, feed_id: int) -> list[FeedItem]:
        pass

    @abstractmethod
    def get_active_feed_items_by_feed_id(
        self,
        feed_id: int,
        title_search: str = '',
        limit: int | None = 20,
        offset: int = 0,
        last_day: bool = False,
        only_unread_items: bool = False,
        only_starred_items: bool = False,
        rss_items: bool = False
    ) -> list[FeedItem]:
        pass

    @abstractmethod
    def count_active_feed_items_by_feed_id(
        self,
        feed_id: int,
        title_search: str,
        read: bool | None = None,
        last_day: bool = False,
        is_starred: bool = False
    ) -> int:
        pass

    @abstractmethod
    def get_feed_item_by_feed_item_external_id(
        self,
        feed_item_external_id: UUID
    ) -> FeedItem | None:
        pass

    @abstractmethod
    def get_feed_item_by_id(self, id: int) -> FeedItem | None:
        pass

    @abstractmethod
    def create_feed_item(self, feed_item_request: FeedItemRequest) -> FeedItem:
        pass

    @abstractmethod
    def update_feed_item(
        self,
        feed_item_external_id: int,
        update_feed_item_request: UpdateFeedItemRequest
    ) -> FeedItem:
        pass

    @abstractmethod
    def update_feed_items(
        self,
        feed_id: int,
        update_feed_items_request: UpdateFeedItemsRequest
    ) -> bool:
        pass

    @abstractmethod
    def delete_feed_item(self, feed_item_id: int) -> bool:
        pass

    @abstractmethod
    def get_number_of_feed_items_by_feed_id(self, feed_id: int) -> int:
        pass

    @abstractmethod
    def set_feed_item_as_inactive(self, feed_item_id: int) -> bool:
        pass

    @abstractmethod
    def set_updated_at(self, feed_id: int) -> datetime:
        pass
