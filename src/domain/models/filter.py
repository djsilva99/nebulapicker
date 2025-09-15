from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Operation(str, Enum):
    identity = "identity"


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
