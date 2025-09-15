from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.models.source import Source, SourceRequest


class SourcePort(ABC):

    @abstractmethod
    def create(self, source_request: SourceRequest) -> Source:
        pass

    @abstractmethod
    def get_all(self) -> list[Source]:
        pass

    @abstractmethod
    def get_by_external_id(self, external_id: UUID) -> Source | None:
        pass

    @abstractmethod
    def get_by_url(self, url: str) -> Source | None:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Source | None:
        pass
