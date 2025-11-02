from pydantic import BaseModel
from src.domain.models.filter import Filter, FilterRequest, Operation


class FilterItem(BaseModel):
    operation: Operation
    args: str


class CreateFilterRequest(BaseModel):
    picker_id: int
    operation: Operation
    args: str


def map_create_filter_request_to_filter_request(
    create_filter_request: CreateFilterRequest
) -> FilterRequest:
    return FilterRequest(
        picker_id=create_filter_request.picker_id,
        operation=create_filter_request.operation,
        args=create_filter_request.args
    )


def map_filter_to_filter_item(
    filter: Filter
) -> FilterItem:
    return FilterItem(
        operation=filter.operation,
        args=filter.args
    )


def map_filter_item_to_create_filter_request(
    filter_item: FilterItem,
    picker_id: int
) -> CreateFilterRequest:
    return CreateFilterRequest(
        operation=filter_item.operation,
        args=filter_item.args,
        picker_id=picker_id
    )
