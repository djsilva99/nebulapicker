from abc import ABC, abstractmethod

from src.domain.models.source import Source


class SourcePort(ABC):
    """
    Abstract Base Class (Port) for the Source repository.
    This defines the contract for how the repository should behave.
    """
    @abstractmethod
    def get_by_id(self, source_id: int) -> Source | None:
        """Retrieve a source record by its ID."""
        pass

    @abstractmethod
    def get_all(self) -> list[Source]:
        """Retrieve a source record by its ID."""
        pass
