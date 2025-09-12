from abc import ABC, abstractmethod

from src.domain.models.source import Source


class SourcePort(ABC):

    @abstractmethod
    def get_by_id(self, source_id: int) -> Source | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Source]:
        pass
