import logging
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Response, status

from src.adapters.entrypoints.v1.models.feeds import (
    CreateFeedRequest,
    CreateFeedResponse,
    FullCompleteFeed,
    ListFeedsResponse,
    map_feed_item_to_external_feed_item,
    map_feed_to_create_feed_response,
    map_feeds_list_to_list_feeds_response,
)
from src.adapters.entrypoints.v1.models.filter import (
    map_create_filter_request_to_filter_request,
    map_filter_item_to_create_filter_request,
    map_filter_to_filter_item,
)
from src.adapters.entrypoints.v1.models.logs import APILog
from src.adapters.entrypoints.v1.models.picker import (
    CreateFullPickerRequest,
    FullFeedPickerResponse,
    FullPickerResponse,
)
from src.adapters.entrypoints.v1.models.source import (
    GetAllSourcesResponse,
    map_source_list_to_get_all_sources_response,
)
from src.adapters.entrypoints.v1.models.welcome import WelcomeResponse
from src.adapters.repositories.feeds_repository import FeedsRepository
from src.adapters.repositories.filters_repository import FiltersRepository
from src.adapters.repositories.pickers_repository import PickersRepository
from src.adapters.repositories.sources_repository import SourcesRepository
from src.adapters.scheduler import Scheduler
from src.configs.database import get_db
from src.configs.dependencies.services import (
    get_feed_service,
    get_filter_service,
    get_job_service,
    get_picker_service,
    get_source_service,
)
from src.configs.settings import Settings
from src.domain.models.feed import FeedRequest
from src.domain.models.picker import PickerRequest
from src.domain.models.source import SourceRequest
from src.domain.services.feed_service import FeedService
from src.domain.services.filter_service import FilterService
from src.domain.services.job_service import JobService
from src.domain.services.picker_service import PickerService
from src.domain.services.source_service import SourceService

# CONSTANTS
settings: Settings = Settings()


# LOGGING CONFIGURATION
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# API
app = FastAPI(
    title="NebulaPicker",
    description="API for NebulaPicker — manage sources, feeds, pickers and scheduled jobs.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# SCHEDULER
scheduler_adapter = Scheduler()


@app.on_event("startup")
def startup():
    db_session = next(get_db())
    feed_repository = FeedsRepository(db_session)
    source_repository = SourcesRepository(db_session)
    picker_repository = PickersRepository(db_session)
    filter_repository = FiltersRepository(db_session)
    feed_service = FeedService(feeds_port=feed_repository)
    source_service = SourceService(source_port=source_repository)
    picker_service = PickerService(pickers_port=picker_repository)
    filter_service = FilterService(filters_port=filter_repository)
    job_service = JobService(
        feed_service=feed_service,
        source_service=source_service,
        picker_service=picker_service,
        filter_service=filter_service,
        scheduler=scheduler_adapter
    )
    app.state.job_service = job_service
    scheduler_adapter.start()
    job_service.load_all()

@app.on_event("shutdown")
def shutdown():
    scheduler_adapter.shutdown()

@app.get(
    "/v1",
    summary="Welcome",
    description="Return a welcome message for the API.",
    response_model=WelcomeResponse,
    tags=["General"]
)
def welcome():
    """
    Welcome endpoint. Returns a short welcome message.
    """
    message_collection = WelcomeResponse()
    logger.info(APILog.WELCOME_SUCCESS)
    return message_collection


@app.get(
    "/v1/sources",
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


@app.post(
    "/v1/feeds/",
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
) -> CreateFeedResponse:
    feed_request = FeedRequest(name=create_feed_request.name)
    created_feed = feed_service.create_feed(feed_request)
    return map_feed_to_create_feed_response(created_feed)


@app.get(
    "/v1/feeds/",
    summary="List Feeds",
    description="Return all feeds.",
    tags=["Feeds"],
    responses={
        200: {
            "description": "List feeds",
            "content": {
                "application/json": {
                    "schema": {
                        "$ref": "#/components/schemas/ListFeedResponse"
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


@app.get(
    "/v1/feeds/{external_id}.xml",
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
    return Response(
        content=feeds_rss,
        media_type="application/rss+xml",
        headers={"Content-Disposition": f'inline; filename="{external_id}.xml"'}
    )


@app.get(
    "/v1/feeds/{external_id}",
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


@app.post(
    "/v1/pickers/",
    status_code=status.HTTP_201_CREATED,
    summary="Create picker (full)",
    description="Create a picker, optionally creating a feed and source, and attach filters.",
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
        source = source_service.create_source(
            SourceRequest(
                url=create_full_picker_request.source_url
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


@app.get(
    "/v1/pickers/{picker_external_id}",
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
    """
    Get picker details by external id.
    """
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


@app.delete(
    "/v1/pickers/{picker_external_id}",
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
