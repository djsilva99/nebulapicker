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
    updated_at: datetime


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
    content: str | None = None
    reading_time: int | None = None
    image_url: str | None = None


class FeedItemRequest(BaseModel):
    link: str
    feed_id: int
    author: str = ""
    created_at: datetime | None = None
    title: str = ""
    description: str = ""
    content: str = ""
    reading_time: int = 0
    image_url: str | None = None


class FeedItemContent(BaseModel):
    title: str
    content: str | None = None
    image_url: str | None = None
    reading_time: int | None = None


class FeedItemImageUrl(BaseModel):
    url: str


class GetFeedItemContentRequest(BaseModel):
    url: str


class GetFeedItemImageUrlRequest(BaseModel):
    url: str
