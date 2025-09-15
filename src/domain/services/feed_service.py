from src.domain.models.feed import Feed, FeedRequest
from src.domain.ports.feeds_port import FeedsPort


class FeedService:
    def __init__(self, feeds_port: FeedsPort):
        self.feeds_port = feeds_port

    def create_feed(self, feed_request: FeedRequest) -> Feed:
        return self.feeds_port.create(feed_request)

    def get_all_feeds(self) -> list[Feed]:
        return self.feeds_port.get_all()

    def get_feed_by_external_id(self, external_id) -> Feed | None:
        return self.feeds_port.get_by_external_id(external_id)

    def get_feed_by_id(self, id: int) -> Feed | None:
        return self.feeds_port.get_by_id(id)
