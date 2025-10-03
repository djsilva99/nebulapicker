from uuid import UUID

from feedgenerator import Rss201rev2Feed
from src.domain.models.feed import Feed, FeedItem, FeedItemRequest, FeedRequest
from src.domain.ports.feeds_port import FeedsPort


class FeedService:
    def __init__(self, feeds_port: FeedsPort):
        self.feeds_port = feeds_port

    def create_feed(self, feed_request: FeedRequest) -> Feed:
        return self.feeds_port.create_feed(feed_request)

    def get_all_feeds(self) -> list[Feed]:
        return self.feeds_port.get_all_feeds()

    def get_feed_by_external_id(self, external_id: UUID) -> Feed | None:
        return self.feeds_port.get_feed_by_external_id(external_id)

    def get_feed_by_id(self, id: int) -> Feed | None:
        return self.feeds_port.get_feed_by_id(id)

    def get_feed_items(self, feed_id: int) -> list[FeedItem]:
        return self.feeds_port.get_feed_items_by_feed_id(feed_id)

    def create_feed_item(self, feed_item_request: FeedItemRequest):
        return self.feeds_port.create_feed_item(feed_item_request)

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
        for feed_item in feed_items:
            feed_object.add_item(
                title=feed_item.title,
                link=feed_item.link,
                description=feed_item.description,
                author_name=feed_item.author,
                pubdate=feed_item.created_at
            )

        return feed_object.writeString("utf-8")
