import logging

from fastapi import Depends, FastAPI, status

from src.adapters.entrypoints.v1.models.feeds import (
    CreateFeedRequest,
    map_feed_to_create_feed_response,
    map_feeds_list_to_list_feeds_response,
)
from src.adapters.entrypoints.v1.models.job import CreateJobRequest, CreateJobResponse
from src.adapters.entrypoints.v1.models.logs import APILog
from src.adapters.entrypoints.v1.models.source import (
    GetAllSourcesResponse,
    map_source_list_to_get_all_sources_response,
)
from src.adapters.entrypoints.v1.models.welcome import WelcomeResponse
from src.adapters.repositories.jobs_repository import JobRepository
from src.adapters.scheduler import Scheduler
from src.configs.database import get_db
from src.configs.dependencies.services import get_feed_service, get_job_service, get_source_service
from src.configs.settings import Settings
from src.domain.models.feed import FeedRequest
from src.domain.models.job import JobRequest
from src.domain.services.feed_service import FeedService
from src.domain.services.job_service import JobService
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
    job_repository = JobRepository(db_session)
    job_service = JobService(job_port=job_repository, scheduler=scheduler_adapter)
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

@app.post("/v1/pickers/", status_code=status.HTTP_201_CREATED)
def add_cronjob(
    job_request: CreateJobRequest,
    job_service: JobService = Depends(get_job_service) # noqa: B008
):
    cronjob = JobRequest(
        func_name=job_request.func_name,
        schedule=job_request.schedule,
        args=job_request.args,
    )
    job_service.add_cronjob(cronjob)
    return CreateJobResponse()
