from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.models.feed import Feed, FeedRequest


class FeedsPort(ABC):

    @abstractmethod
    def create(self, feed_request: FeedRequest) -> Feed:
        pass

    @abstractmethod
    def get_all(self) -> list[Feed]:
        pass

    @abstractmethod
    def get_by_external_id(self, external_id: UUID) -> Feed | None:
        pass
