from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from src.adapters.entrypoints.v1.models.feeds import (
    CreateFeedRequest,
    ExternalUpdateFeedRequest,
    FeedResponse,
    FullCompleteFeed,
    ListFeedsResponse,
    map_feed_item_to_external_feed_item,
    map_feed_to_feed_response,
    map_feeds_list_to_list_feeds_response,
)
from src.adapters.entrypoints.v1.models.filter import (
    map_create_filter_request_to_filter_request,
    map_filter_item_to_create_filter_request,
    map_filter_to_filter_item,
)
from src.adapters.entrypoints.v1.models.picker import (
    CreateFullPickerRequest,
    FullFeedPickerResponse,
    FullPickerResponse,
)
from src.adapters.entrypoints.v1.models.source import (
    ExternalSourceRequest,
    GetAllSourcesResponse,
    SourceResponse,
    map_source_list_to_get_all_sources_response,
    map_source_to_create_source_response,
)
from src.configs.dependencies.services import (
    get_feed_service,
    get_filter_service,
    get_job_service,
    get_picker_service,
    get_source_service,
)
from src.domain.models.feed import FeedRequest, UpdateFeedRequest
from src.domain.models.picker import PickerRequest
from src.domain.models.source import SourceRequest
from src.domain.services.feed_service import FeedService
from src.domain.services.filter_service import FilterService
from src.domain.services.job_service import JobService
from src.domain.services.picker_service import PickerService
from src.domain.services.source_service import SourceService

router = APIRouter(prefix="/v1")


@router.get(
    "/sources",
    summary="List Sources",
    description="Return all configured sources.",
    response_model=GetAllSourcesResponse,
    tags=["Sources"],
    responses={
        200: {
            "description": "List of sources",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/GetAllSourcesResponse"
                    }
                }
            }
        }
    }
)
def list_sources(
    source_service: SourceService = Depends(get_source_service)  # noqa: B008
) -> GetAllSourcesResponse:
    source_list = source_service.get_all_sources()
    return GetAllSourcesResponse(
        sources=map_source_list_to_get_all_sources_response(source_list=source_list)
    )


@router.post(
    "/sources",
    status_code=status.HTTP_201_CREATED,
    summary="Create Source",
    description="Create a new source with the given name.",
    tags=["Sources"],
    responses={
        201: {
            "description": "Source created",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/SourceResponse"
                    }
                }
            }
        },
        422: {"description": "Validation error"}
    }
)
def create_source(
    create_source_request: ExternalSourceRequest,
    source_service: SourceService = Depends(get_source_service)  # noqa: B008
) -> SourceResponse:
    source_request = SourceRequest(name=create_source_request.name, url=create_source_request.url)
    created_source = source_service.create_source(source_request)
    return map_source_to_create_source_response(created_source)


@router.get(
    "/sources/{source_external_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Source",
    description="Get an existing source by its ID.",
    tags=["Sources"],
    responses={
        200: {
            "description": "Source updated",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/SourceResponse"
                    }
                }
            }
        },
        404: {"description": "Source not found"},
        422: {"description": "Validation error"}
    }
)
def get_source(
    source_external_id: UUID,
    source_service: SourceService = Depends(get_source_service)  # noqa: B008
) -> SourceResponse:
    source = source_service.get_source_by_external_id(
        source_external_id
    )
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return map_source_to_create_source_response(source)


@router.put(
    "/sources/{source_external_id}",
    status_code=status.HTTP_200_OK,
    summary="Update Source",
    description="Update an existing source by its ID.",
    tags=["Sources"],
    responses={
        200: {
            "description": "Source updated",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/SourceResponse"
                    }
                }
            }
        },
        404: {"description": "Source not found"},
        422: {"description": "Validation error"}
    }
)
def update_source(
    source_external_id: UUID,
    update_source_request: ExternalSourceRequest,
    source_service: SourceService = Depends(get_source_service),  # noqa: B008
) -> SourceResponse:
    source_request = SourceRequest(
        name=update_source_request.name,
        url=update_source_request.url
    )
    updated_source = source_service.update_source(
        source_external_id,
        source_request
    )
    if updated_source is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return map_source_to_create_source_response(updated_source)


@router.delete(
    "/sources/{source_external_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete source",
    description="Delete a source by external id.",
    tags=["Sources"],
    responses={204: {"description": "Deleted"}, 404: {"description": "Source not found"}}
)
def delete_source(
    source_external_id: UUID,
    source_service: SourceService = Depends(get_source_service),  # noqa: B008
    filter_service: FilterService = Depends(get_filter_service),  # noqa: B008
    picker_service: PickerService = Depends(get_picker_service),  # noqa: B008
):
    source = source_service.get_source_by_external_id(
        external_id=source_external_id
    )
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # delete pickers and filters
    pickers = picker_service.get_pickers_by_source_id(source.id)
    for picker in pickers:
        filters = filter_service.get_filters_by_picker_id(picker.id)
        for filter in filters:
            filter_service.delete_filter(filter.id)
        picker_service.delete_picker(picker.id)
    source_service.delete_source(source.id)
    return None


@router.get(
    "/feeds",
    summary="List Feeds",
    description="Return all feeds.",
    tags=["Feeds"],
    responses={
        200: {
            "description": "List feeds",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ListFeedsResponse"
                    }
                }
            }
        }
    }
)
def list_feeds(
    feed_service: FeedService = Depends(get_feed_service)  # noqa: B008
) -> ListFeedsResponse:
    feeds_list = feed_service.get_all_feeds()

    return map_feeds_list_to_list_feeds_response(feeds_list)


@router.post(
    "/feeds",
    status_code=status.HTTP_201_CREATED,
    summary="Create Feed",
    description="Create a new feed with the given name.",
    tags=["Feeds"],
    responses={
        201: {
            "description": "Feed created",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/CreateFeedResponse"
                    }
                }
            }
        },
        422: {"description": "Validation error"}
    }
)
def create_feed(
    create_feed_request: CreateFeedRequest,
    feed_service: FeedService = Depends(get_feed_service)  # noqa: B008
) -> FeedResponse:
    feed_request = FeedRequest(name=create_feed_request.name)
    created_feed = feed_service.create_feed(feed_request)
    return map_feed_to_feed_response(created_feed)


@router.patch(
    "/feeds/{feed_external_id}",
    status_code=status.HTTP_200_OK,
    summary="Update Feed",
    description="Update fields of an existing feed.",
    tags=["Feeds"],
    responses={
        201: {
            "description": "Feed updated",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/FeedResponse"
                    }
                }
            }
        },
        404: {"description": "Feed not found"},
        422: {"description": "Validation error"}
    }
)
def update_feed(
    feed_external_id: UUID,
    update_feed_request: ExternalUpdateFeedRequest,
    feed_service: FeedService = Depends(get_feed_service)  # noqa: B008
) -> FeedResponse:
    update_feed_request = UpdateFeedRequest(
        name=update_feed_request.name
    )
    updated_feed = feed_service.update_feed(
        feed_external_id,
        update_feed_request
    )
    if updated_feed is None:
        raise HTTPException(status_code=404, detail="Feed not found")
    return map_feed_to_feed_response(updated_feed)


@router.delete(
    "/feeds/{feed_external_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete feed",
    description="Delete a feed by external id (and cascade deletes).",
    tags=["Feeds"],
    responses={204: {"description": "Deleted"}, 404: {"description": "Feed not found"}}
)
def delete_feed(
    feed_external_id: UUID,
    feed_service: FeedService = Depends(get_feed_service),  # noqa: B008
    filter_service: FilterService = Depends(get_filter_service),  # noqa: B008
    picker_service: PickerService = Depends(get_picker_service),  # noqa: B008
):
    feed = feed_service.get_feed_by_external_id(external_id=feed_external_id)
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    pickers = picker_service.get_pickers_by_feed_id(feed.id)
    for picker in pickers:
        for filter in filter_service.get_filters_by_picker_id(
            picker_id=picker.id
        ):
            filter_service.delete_filter(filter.id)
        picker_service.delete_picker(picker_id=picker.id)

    feed_items = feed_service.get_feed_items(feed.id)
    for feed_item in feed_items:
        feed_service.delete_feed_item(feed_item.id)
    feed_service.delete_feed(feed.id)
    return None


@router.get(
    "/feeds/{external_id}.xml",
    summary="Get RSS for feed",
    description="Return the RSS XML for the feed identified by external_id.",
    tags=["Feeds"],
    responses={
        200: {
            "description": "RSS XML (application/rss+xml)",
            "content": {
                "application/rss+xml": {
                    "example": "<?xml version='1.0' encoding='utf-8'?><rss>...</rss>"
                }
            }
        },
        404: {"description": "Feed not found"}
    }
)
def get_feed_rss(
    external_id: UUID,
    feed_service: FeedService = Depends(get_feed_service)  # noqa: B008
):
    """
    Returns raw RSS XML for the requested feed.
    The response content type is `application/rss+xml`.
    """
    feeds_rss = feed_service.get_rss(external_id)
    if feeds_rss:
        return Response(
            content=feeds_rss,
            media_type="application/rss+xml",
            headers={"Content-Disposition": f'inline; filename="{external_id}.xml"'}
        )
    raise HTTPException(status_code=404, detail="Feed not found")


@router.get(
    "/feeds/{external_id}",
    summary="Get full feed data",
    description="Return feed metadata, pickers, filters and feed items for the given feed.",
    response_model=FullCompleteFeed,
    tags=["Feeds"],
    responses={
        200: {
            "description": "Full feed details",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/FullCompleteFeed"
                    }
                }
            }
        },
        404: {"description": "Feed not found"}
    }
)
def get_feed(
    external_id: UUID,
    feed_service: FeedService = Depends(get_feed_service),  # noqa: B008
    filter_service: FilterService = Depends(get_filter_service),  # noqa: B008
    picker_service: PickerService = Depends(get_picker_service),  # noqa: B008
    source_service: SourceService = Depends(get_source_service),  # noqa: B008
) -> FullCompleteFeed:
    feed = feed_service.get_feed_by_external_id(external_id)
    if not feed:
        raise HTTPException(status_code=404, detail="Feed not found")

    # build pickers list
    pickers = picker_service.get_pickers_by_feed_id(feed.id)
    picker_items = []
    for picker in pickers:
        source_url = source_service.get_source_by_id(picker.source_id).url
        filters = filter_service.get_filters_by_picker_id(picker.id)
        filter_items = [map_filter_to_filter_item(f) for f in filters]
        picker_items.append(
            FullFeedPickerResponse(
                cronjob=picker.cronjob,
                source_url=source_url,
                filters=filter_items,
                external_id=picker.external_id,
                created_at=picker.created_at,
            )
        )

    feed_items = feed_service.get_feed_items(feed.id)
    external_feed_items = [map_feed_item_to_external_feed_item(fi) for fi in feed_items]

    return FullCompleteFeed(
        name=feed.name,
        external_id=feed.external_id,
        created_at=feed.created_at,
        pickers=picker_items,
        feed_items=external_feed_items,
    )


@router.post(
    "/pickers",
    status_code=status.HTTP_201_CREATED,
    summary="Create picker (full)",
    description="Create a picker and its dependencies.",
    response_model=FullPickerResponse,
    tags=["Pickers"],
    responses={
        201: {
            "description": "Picker created",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/FullPickerResponse"
                    }
                }
            }
        },
        400: {"description": "Bad request / validation error"}
    }
)
def add_picker(
    create_full_picker_request: CreateFullPickerRequest,
    filter_service: FilterService = Depends(get_filter_service),  # noqa: B008
    picker_service: PickerService = Depends(get_picker_service),  # noqa: B008
    source_service: SourceService = Depends(get_source_service),  # noqa: B008
    feed_service: FeedService = Depends(get_feed_service),  # noqa: B008
    job_service: JobService = Depends(get_job_service),  # noqa: B008
) -> FullPickerResponse:

    feed_name = None
    if create_full_picker_request.feed_name:
        feed_name = create_full_picker_request.feed_name

    # get or create feed
    feed = None
    if create_full_picker_request.feed_external_id:
        feed = feed_service.get_feed_by_external_id(
            create_full_picker_request.feed_external_id
        )
        if not feed:
            raise HTTPException(status_code=400, detail="Feed not found")
    else:
        feed = feed_service.create_feed(
            FeedRequest(
                name=feed_name
            )
        )

    # get or create source
    source = source_service.get_source_by_url(
        create_full_picker_request.source_url
    )
    if not source:
        url = create_full_picker_request.source_url
        source_name = url.split('//')[1].split('/')[0]
        source = source_service.create_source(
            SourceRequest(
                url=create_full_picker_request.source_url,
                name=source_name
            )
        )

    # create picker
    created_picker = picker_service.create_picker(
        PickerRequest(
            cronjob=create_full_picker_request.cronjob,
            source_id=source.id,
            feed_id=feed.id
        )
    )

    # create filters
    filters = create_full_picker_request.filters
    filters_response = []
    for filter_item in filters:
        filters_response.append(
            map_filter_to_filter_item(
                filter_service.create_filter(
                    map_create_filter_request_to_filter_request(
                        map_filter_item_to_create_filter_request(
                            filter_item,
                            created_picker.id
                        )
                    )
                )
            )
        )

    # create cronjob
    job_service.add_cronjob(created_picker)

    return FullPickerResponse(
        external_id=created_picker.external_id,
        cronjob=created_picker.cronjob,
        source_url=source.url,
        feed_external_id=feed.external_id,
        created_at=created_picker.created_at,
        filters=filters_response
    )


@router.get(
    "/pickers/{picker_external_id}",
    status_code=status.HTTP_200_OK,
    summary="Get picker",
    description="Return a picker and its filters by external id.",
    response_model=FullPickerResponse,
    tags=["Pickers"],
    responses={
        200: {
            "description": "Picker details",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/FullPickerResponse"
                    }
                }
            }
        },
        404: {
            "description": "Picker not found"
        }
    }
)
def get_picker(
    picker_external_id: UUID,
    filter_service: FilterService = Depends(get_filter_service),  # noqa: B008
    picker_service: PickerService = Depends(get_picker_service),  # noqa: B008
    feed_service: FeedService = Depends(get_feed_service),  # noqa: B008
    source_service: SourceService = Depends(get_source_service),  # noqa: B008
) -> FullPickerResponse | None:
    picker = picker_service.get_picker_by_external_id(external_id=picker_external_id)
    if not picker:
        raise HTTPException(status_code=404, detail="Picker not found")

    source = source_service.get_source_by_id(picker.source_id)
    feed = feed_service.get_feed_by_id(picker.feed_id)
    filters = filter_service.get_filters_by_picker_id(picker.id)
    filter_items = [map_filter_to_filter_item(f) for f in filters]

    return FullPickerResponse(
        external_id=picker.external_id,
        cronjob=picker.cronjob,
        source_url=source.url,
        feed_external_id=feed.external_id,
        created_at=picker.created_at,
        filters=filter_items,
    )


@router.delete(
    "/pickers/{picker_external_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete picker",
    description="Delete a picker by external id (and cascade delete its filters).",
    tags=["Pickers"],
    responses={204: {"description": "Deleted"}, 404: {"description": "Picker not found"}}
)
def delete_picker(
    picker_external_id: UUID,
    filter_service: FilterService = Depends(get_filter_service),  # noqa: B008
    picker_service: PickerService = Depends(get_picker_service),  # noqa: B008
):
    picker = picker_service.get_picker_by_external_id(external_id=picker_external_id)
    if not picker:
        raise HTTPException(status_code=404, detail="Picker not found")

    for filter in filter_service.get_filters_by_picker_id(picker_id=picker.id):
        filter_service.delete_filter(filter.id)

    picker_service.delete_picker(picker_id=picker.id)
    return None
