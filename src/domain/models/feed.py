from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FeedRequest(BaseModel):
    name: str


class Feed(BaseModel):
    id: int
    external_id: UUID
    name: str
    created_at: datetime
