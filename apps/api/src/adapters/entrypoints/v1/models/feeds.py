from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel
from src.adapters.entrypoints.v1.models.picker import FullFeedPickerResponse
from src.domain.models.feed import DetailedFeed, Feed, FeedItem, FeedRequest


class ExportFileType(str, Enum):
    epub = "epub"
    pdf = "pdf"


class CreateFeedRequest(BaseModel):
    name: str

    class Config:
        extra = "forbid"

class FeedResponse(BaseModel):
    name: str
    external_id: UUID
    created_at: datetime


class ExternalFeeds(BaseModel):
    name: str
    external_id: UUID
    created_at: datetime
    latest_item_datetime: datetime
    number_of_feed_items: int


class ListFeedsResponse(BaseModel):
    feeds: list[ExternalFeeds]


class ExternalUpdateFeedRequest(BaseModel):
    name: str | None = None

    class Config:
        extra = "forbid"


class ExternalFeedItem(BaseModel):
    external_id: UUID
    link: str
    title: str
    author: str
    reading_time: int
    created_at: datetime
    image_url: str | None


class CreateFeedItemResponse(BaseModel):
    external_id: UUID
    link: str
    title: str
    author: str
    created_at: datetime


class GetFeedItemResponse(BaseModel):
    external_id: UUID
    link: str
    title: str
    author: str
    content: str
    reading_time: int
    created_at: datetime


class FullCompleteFeed(BaseModel):
    name: str
    external_id: UUID
    created_at: datetime
    pickers: list[FullFeedPickerResponse]
    feed_items: list[ExternalFeedItem]


class CreateFeedItemRequest(BaseModel):
    link: str
    title: str
    description: str
    content: str
    created_at: datetime | None = None


class ExportFeedItemsRequest(BaseModel):
    file_type: ExportFileType
    start_time: datetime
    end_time: datetime


def map_create_feed_request_to_feed_request(
    create_feed_request: CreateFeedRequest
) -> FeedRequest:
    return FeedRequest(
        name=create_feed_request.name,
    )


def map_feed_to_feed_response(
    feed: Feed
) -> FeedResponse:
    return FeedResponse(
        name=feed.name,
        external_id=feed.external_id,
        created_at=feed.created_at
    )


def map_detailed_feeds_list_to_list_feeds_response(
    detailed_feeds_list: list[DetailedFeed]
) -> ListFeedsResponse:
    return ListFeedsResponse(
        feeds=[
            ExternalFeeds(
                name=feed.name if feed.name else "",
                external_id=feed.external_id,
                created_at=feed.created_at,
                latest_item_datetime=feed.latest_item_datetime,
                number_of_feed_items=feed.number_of_feed_items
            )
            for feed in detailed_feeds_list
        ]
    )


def map_feed_item_to_external_feed_item(
    feed_item: FeedItem
):
    return ExternalFeedItem(
        external_id=feed_item.external_id,
        link=feed_item.link,
        title=feed_item.title,
        author=feed_item.author,
        created_at=feed_item.created_at,
        reading_time=feed_item.reading_time,
        image_url=feed_item.image_url
    )


def map_feed_item_to_create_feed_item_response(
    feed_item: FeedItem
):
    return CreateFeedItemResponse(
        external_id=feed_item.external_id,
        link=feed_item.link,
        title=feed_item.title,
        author=feed_item.author,
        created_at=feed_item.created_at,
    )


def map_feed_item_to_get_feed_item_response(
    feed_item: FeedItem
):
    return GetFeedItemResponse(
        external_id=feed_item.external_id,
        link=feed_item.link,
        title=feed_item.title,
        author=feed_item.author,
        created_at=feed_item.created_at,
        content=feed_item.content,
        reading_time=feed_item.reading_time
    )
