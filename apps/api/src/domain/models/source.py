from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SourceRequest(BaseModel):
    url: str
    name: str | None = None


class Source(BaseModel):
    id: int
    external_id: UUID
    url: str
    name: str | None
    created_at: datetime
