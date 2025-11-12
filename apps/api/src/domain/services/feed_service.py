import datetime
from uuid import UUID

from feedgenerator import Rss201rev2Feed
from src.domain.models.feed import (
    DetailedFeed,
    Feed,
    FeedItem,
    FeedItemRequest,
    FeedRequest,
    UpdateFeedRequest,
)
from src.domain.ports.feeds_port import FeedsPort

MAX_NUMBER_OF_ITEMS = 50
HOURS_TO_COMPARE = 24


class FeedService:
    def __init__(self, feeds_port: FeedsPort):
        self.feeds_port = feeds_port

    def create_feed(self, feed_request: FeedRequest) -> Feed:
        return self.feeds_port.create_feed(feed_request)

    def update_feed(
        self,
        feed_external_id: UUID,
        update_feed_request: UpdateFeedRequest
    ) -> Feed:
        feed = self.get_feed_by_external_id(feed_external_id)
        if feed is None:
            return None
        return self.feeds_port.update_feed(feed.id, update_feed_request)

    def delete_feed(self, feed_id: int) -> bool:
        return self.feeds_port.delete_feed(feed_id)

    def get_feed_item_by_external_id(self, feed_item_external_id: UUID):
        return self.feeds_port.get_feed_item_by_feed_item_external_id(feed_item_external_id)

    def get_all_feeds(self) -> list[Feed]:
        return sorted(self.feeds_port.get_all_feeds(), key=lambda item: item.name)

    def get_detailed_feeds(self) -> list[DetailedFeed]:
        feeds = self.feeds_port.get_all_feeds()
        detailed_feeds = []
        for feed in feeds:
            feed_items = self.feeds_port.get_feed_items_by_feed_id(feed.id)
            number_of_feed_items = len(feed_items)
            latest_item_datetime = sorted(
                feed_items,
                key=lambda item: item.created_at
            )[-1].created_at
            detailed_feeds.append(
                DetailedFeed(
                    id=feed.id,
                    external_id=feed.external_id,
                    name=feed.name,
                    created_at=feed.created_at,
                    latest_item_datetime=latest_item_datetime,
                    number_of_feed_items=number_of_feed_items
                )
            )
        return sorted(detailed_feeds, key=lambda item: item.name)

    def get_feed_by_external_id(self, external_id: UUID) -> Feed | None:
        return self.feeds_port.get_feed_by_external_id(external_id)

    def get_feed_by_id(self, id: int) -> Feed | None:
        return self.feeds_port.get_feed_by_id(id)

    def get_feed_items(self, feed_id: int, title: str | None = None) -> list[FeedItem]:
        feed_items = sorted(
            self.feeds_port.get_feed_items_by_feed_id(feed_id),
            key=lambda item: item.created_at
        )
        if title:
            feeds_to_return = []
            for feed_item in feed_items:
                if (
                    feed_item.title == title and
                    feed_item.created_at >= (
                        datetime.datetime.now() - datetime.timedelta(hours=HOURS_TO_COMPARE)
                    )
                ):
                    feeds_to_return.append(feed_item)
            return feeds_to_return
        return feed_items

    def create_feed_item(self, feed_item_request: FeedItemRequest):
        return self.feeds_port.create_feed_item(feed_item_request)

    def delete_feed_item(self, feed_item_id: int) -> bool:
        return self.feeds_port.delete_feed_item(feed_item_id)

    def get_rss(self, feed_external_id: UUID) -> str | None:
        feed = self.feeds_port.get_feed_by_external_id(feed_external_id)
        if not feed:
            return None
        feed_items = self.feeds_port.get_feed_items_by_feed_id(feed.id)
        feed_object = Rss201rev2Feed(
            title=feed.name,
            link="http://127.0.0.1:8080/" + str(feed.external_id),
            description=feed.name,
            language="en",
        )
        for feed_item in feed_items[:MAX_NUMBER_OF_ITEMS]:
            feed_object.add_item(
                title=feed_item.title,
                link=feed_item.link,
                description=feed_item.description,
                author_name=feed_item.author,
                pubdate=feed_item.created_at
            )

        return feed_object.writeString("utf-8")
