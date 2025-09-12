from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Source(BaseModel):
    id: int
    external_id: UUID
    url: str
    name: str
    created_at: datetime
