from src.domain.models.feed import FeedItemContent, GetFeedItemContentRequest
from src.domain.ports.extractor_port import ExtractorPort


class ExtractorService:
    def __init__(self, extractor_port: ExtractorPort):
        self.extractor_port = extractor_port

    def extract_feed_item_content(
        self,
        feed_item_content_request: GetFeedItemContentRequest
    ) -> FeedItemContent | None:
        return self.extractor_port.get_feed_item_content(
            feed_item_content_request
        )
