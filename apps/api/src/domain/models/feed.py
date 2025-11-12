from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FeedRequest(BaseModel):
    name: str | None


class UpdateFeedRequest(BaseModel):
    name: str | None = None


class Feed(BaseModel):
    id: int
    external_id: UUID
    name: str | None
    created_at: datetime


class DetailedFeed(BaseModel):
    id: int
    external_id: UUID
    name: str | None
    created_at: datetime
    latest_item_datetime: datetime
    number_of_feed_items: int


class FeedItem(BaseModel):
    id: int
    external_id: UUID
    link: str
    title: str
    description: str
    created_at: datetime
    feed_id: int
    author: str = ""


class FeedItemRequest(BaseModel):
    link: str
    title: str
    description: str
    feed_id: int
    author: str = ""
    created_at: datetime | None = None
