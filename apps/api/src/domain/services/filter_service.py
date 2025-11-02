from src.domain.models.filter import Filter, FilterRequest
from src.domain.ports.filters_port import FiltersPort


class FilterService:
    def __init__(self, filters_port: FiltersPort):
        self.filters_port = filters_port

    def create_filter(self, filter_request: FilterRequest) -> Filter:
        return self.filters_port.create_filter(filter_request)

    def delete_filter(self, filter_id: int) -> bool:
        return self.filters_port.delete_filter(filter_id)

    def get_filters_by_picker_id(self, picker_id: int) -> list[Filter]:
        return self.filters_port.get_filter_by_picker_id(picker_id)
