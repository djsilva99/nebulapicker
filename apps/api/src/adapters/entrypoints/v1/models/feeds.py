from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from src.adapters.entrypoints.v1.models.picker import FullFeedPickerResponse
from src.domain.models.feed import Feed, FeedItem, FeedRequest


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
    created_at: datetime


class FullCompleteFeed(BaseModel):
    name: str
    external_id: UUID
    created_at: datetime
    pickers: list[FullFeedPickerResponse]
    feed_items: list[ExternalFeedItem]



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


def map_feeds_list_to_list_feeds_response(
    feeds_list: list[Feed]
) -> ListFeedsResponse:
    return ListFeedsResponse(
        feeds=[
            ExternalFeeds(
                name=feed.name if feed.name else "",
                external_id=feed.external_id,
                created_at=feed.created_at
            )
            for feed in feeds_list
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
    )
