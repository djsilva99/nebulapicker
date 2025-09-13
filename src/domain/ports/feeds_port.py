from abc import ABC, abstractmethod

from src.domain.models.feed import Feed, FeedRequest


class FeedsPort(ABC):

    @abstractmethod
    def create(self, feed_request: FeedRequest) -> Feed:
        pass

    @abstractmethod
    def get_all(self) -> list[Feed]:
        pass
