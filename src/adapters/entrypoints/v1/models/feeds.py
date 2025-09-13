from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from src.domain.models.feed import Feed, FeedRequest


class CreateFeedRequest(BaseModel):
    name: str


class CreateFeedResponse(BaseModel):
    name: str
    external_id: UUID
    created_at: datetime


class ExternalFeeds(BaseModel):
    name: str
    external_id: UUID
    created_at: datetime


class ListFeedsResponse(BaseModel):
    feeds: list[ExternalFeeds]


def map_create_feed_request_to_feed_request(
    create_feed_request: CreateFeedRequest
) -> FeedRequest:
    return FeedRequest(
        name=create_feed_request.name,
    )


def map_feed_to_create_feed_response(
    feed: Feed
) -> CreateFeedResponse:
    return CreateFeedResponse(
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
                name=feed.name,
                external_id=feed.external_id,
                created_at=feed.created_at
            )
            for feed in feeds_list
        ]
    )
