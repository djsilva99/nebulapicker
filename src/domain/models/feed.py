from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FeedRequest(BaseModel):
    name: str | None


class Feed(BaseModel):
    id: int
    external_id: UUID
    name: str | None
    created_at: datetime
