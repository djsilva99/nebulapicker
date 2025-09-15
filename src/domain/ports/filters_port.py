from abc import ABC, abstractmethod

from src.domain.models.filter import Filter, FilterRequest


class FiltersPort(ABC):

    @abstractmethod
    def create(self, filter_request: FilterRequest) -> Filter:
        pass

    @abstractmethod
    def get_by_picker_id(self, picker_id: int) -> list[Filter]:
        pass
