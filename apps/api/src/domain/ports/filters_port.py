from abc import ABC, abstractmethod

from src.domain.models.filter import Filter, FilterRequest


class FiltersPort(ABC):

    @abstractmethod
    def create_filter(self, filter_request: FilterRequest) -> Filter:
        pass

    @abstractmethod
    def delete_filter(self, filter_id: int) -> bool:
        pass

    @abstractmethod
    def get_filter_by_picker_id(self, picker_id: int) -> list[Filter]:
        pass
