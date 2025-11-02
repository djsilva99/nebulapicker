from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PickerRequest(BaseModel):
    source_id: int
    feed_id: int
    cronjob: str


class Picker(BaseModel):
    id: int
    external_id: UUID
    source_id: int
    feed_id: int
    cronjob: str
    created_at: datetime
