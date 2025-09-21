from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Operation(str, Enum):
    identity = "identity"
    title_contains = "title_contains"
    description_contains = "description_contains"
    title_does_not_contain = "title_does_not_contain"
    description_does_not_contain = "description_does_not_contain"


class Filter(BaseModel):
    id: int
    picker_id: int
    operation: Operation
    args: str | None = None
    created_at: datetime


class FilterRequest(BaseModel):
    picker_id: int
    operation: Operation
    args: str | None = None
