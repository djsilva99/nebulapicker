import logging
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Response, status

from src.adapters.entrypoints.v1.models.feeds import (
    CreateFeedRequest,
    FullCompleteFeed,
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
app = FastAPI()

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

@app.get("/v1")
def welcome():
    message_collection = WelcomeResponse()
    logger.info(
        APILog.WELCOME_SUCCESS,
    )
    return message_collection

@app.get("/v1/sources")
def list_sources(
    source_service: SourceService = Depends(get_source_service) # noqa: B008
):
    source_list = source_service.get_all_sources()
    return GetAllSourcesResponse(
        sources=map_source_list_to_get_all_sources_response(
            source_list=source_list
        )
    )

@app.post("/v1/feeds/", status_code=status.HTTP_201_CREATED)
def create_feed(
    create_feed_request: CreateFeedRequest,
    feed_service: FeedService = Depends(get_feed_service) # noqa: B008
):
    feed_request = FeedRequest(
        name=create_feed_request.name,
    )
    created_feed = feed_service.create_feed(feed_request)
    return map_feed_to_create_feed_response(
        created_feed
    )

@app.get("/v1/feeds/")
def list_feeds(
    feed_service: FeedService = Depends(get_feed_service) # noqa: B008
):
    feeds_list = feed_service.get_all_feeds()
    return map_feeds_list_to_list_feeds_response(
        feeds_list
    )


@app.get("/v1/feeds/{external_id}.xml")
def get_feed_rss(
    external_id: UUID,
    feed_service: FeedService = Depends(get_feed_service) # noqa: B008
):
    feeds_rss = feed_service.get_rss(external_id)

    return Response(
        content=feeds_rss,
        media_type="application/rss+xml",
        headers={
            "Content-Disposition": f'inline; filename="{external_id}.xml"'
        }
    )


@app.get("/v1/feeds/{external_id}")
def get_feed(
    external_id: UUID,
    feed_service: FeedService = Depends(get_feed_service), # noqa: B008
    filter_service: FilterService = Depends(get_filter_service), # noqa: B008
    picker_service: PickerService = Depends(get_picker_service),  # noqa: B008
    source_service: SourceService = Depends(get_source_service), # noqa: B008
):
    # get feeds
    feed = feed_service.get_feed_by_external_id(external_id)

    # get picker
    pickers = picker_service.get_pickers_by_feed_id(feed.id)
    picker_items = []

    for picker in pickers:
        # get source
        source_url = source_service.get_source_by_id(picker.source_id).url
        # get filters
        filters = filter_service.get_filters_by_picker_id(picker.id)
        filter_items = []
        for filter in filters:
            filter_items.append(
                map_filter_to_filter_item(filter)
            )
        picker_items.append(
            FullFeedPickerResponse(
                cronjob=picker.cronjob,
                source_url=source_url,
                filters=filter_items,
                external_id=picker.external_id,
                created_at=picker.created_at
            )
        )

    # get feed_items
    feed_items = feed_service.get_feed_items(feed.id)
    external_feed_items = []
    for feed_item in feed_items:
        external_feed_items.append(
            map_feed_item_to_external_feed_item(
                feed_item
            )
        )

    return FullCompleteFeed(
        name=feed.name,
        external_id=feed.external_id,
        created_at=feed.created_at,
        pickers=picker_items,
        feed_items=external_feed_items
    )


@app.post("/v1/pickers/", status_code=status.HTTP_201_CREATED)
def add_picker(
    create_full_picker_request: CreateFullPickerRequest,
    filter_service: FilterService = Depends(get_filter_service), # noqa: B008
    picker_service: PickerService = Depends(get_picker_service), # noqa: B008
    source_service: SourceService = Depends(get_source_service), # noqa: B008
    feed_service: FeedService = Depends(get_feed_service), # noqa: B008
    job_service: JobService = Depends(get_job_service) # noqa: B008
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

    # return response
    return FullPickerResponse(
        external_id=created_picker.external_id,
        cronjob=created_picker.cronjob,
        source_url=source.url,
        feed_external_id=feed.external_id,
        created_at=created_picker.created_at,
        filters=filters_response
    )

@app.get("/v1/pickers/{picker_external_id}", status_code=status.HTTP_200_OK)
def get_picker(
    picker_external_id: UUID,
    filter_service: FilterService = Depends(get_filter_service), # noqa: B008
    picker_service: PickerService = Depends(get_picker_service), # noqa: B008
    feed_service: FeedService = Depends(get_feed_service), # noqa: B008
    source_service: SourceService = Depends(get_source_service), # noqa: B008
) -> FullPickerResponse | None:
    # picker
    picker = picker_service.get_picker_by_external_id(
        external_id=picker_external_id
    )
    if not picker:
        raise HTTPException(status_code=404, detail="Picker not found")

    # source
    source = source_service.get_source_by_id(
        picker.source_id
    )

    # feed
    feed = feed_service.get_feed_by_id(
        picker.feed_id
    )

    # filters
    filters = filter_service.get_filters_by_picker_id(
        picker_id=picker.id
    )
    filter_items = [
        map_filter_to_filter_item(
            filter
        )
        for filter in filters
    ]

    return FullPickerResponse(
        external_id=picker.external_id,
        cronjob=picker.cronjob,
        source_url=source.url,
        feed_external_id=feed.external_id,
        created_at=picker.created_at,
        filters=filter_items
    )

@app.delete(
    "/v1/pickers/{picker_external_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_picker(
    picker_external_id: UUID,
    filter_service: FilterService = Depends(get_filter_service), # noqa: B008
    picker_service: PickerService = Depends(get_picker_service), # noqa: B008
):
    picker = picker_service.get_picker_by_external_id(external_id=picker_external_id)
    if not picker:
        raise HTTPException(status_code=404, detail="Picker not found")

    # delete filters
    filters = filter_service.get_filters_by_picker_id(picker_id=picker.id)
    for filter in filters:
        filter_service.delete_filter(filter.id)

    # delete picker
    picker_service.delete_picker(picker_id=picker.id)

    return None
