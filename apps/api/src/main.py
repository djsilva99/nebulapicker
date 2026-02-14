import logging

from fastapi import FastAPI, Request
from src.adapters.entrypoints.v1.models.welcome import WelcomeResponse
from src.adapters.entrypoints.v1.routes import router as v1_router
from src.adapters.repositories.feeds_repository import FeedsRepository
from src.adapters.repositories.filters_repository import FiltersRepository
from src.adapters.repositories.pickers_repository import PickersRepository
from src.adapters.repositories.sources_repository import SourcesRepository
from src.adapters.scheduler import Scheduler
from src.adapters.wallabag_extractor import WallabagExtractor
from src.configs.database import get_db
from src.configs.settings import Settings
from src.domain.services.extractor_service import ExtractorService
from src.domain.services.feed_service import FeedService
from src.domain.services.filter_service import FilterService
from src.domain.services.job_service import JobService
from src.domain.services.picker_service import PickerService
from src.domain.services.source_service import SourceService

# CONSTANTS
settings: Settings = Settings()

# API
app = FastAPI(
    title="NebulaPicker",
    description=(
        "NebulaPicker is a self-hosted API for content curation, designed to streamline and "
        "automate the process of filtering online information. It functions as a personalized "
        "feed generator that fetches content from multiple RSS sources, applies user-defined "
        "filters to remove noise, and publishes a new, clean feed tailored to specific interests."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# LOGGING CONFIGURATION
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
app.logger = logging.getLogger(__name__)

# SCHEDULER
scheduler_adapter = Scheduler()


@app.on_event("startup")
def startup():
    db_session = next(get_db())
    feed_repository = FeedsRepository(db_session)
    source_repository = SourcesRepository(db_session)
    picker_repository = PickersRepository(db_session)
    filter_repository = FiltersRepository(db_session)
    wallabag_service = WallabagExtractor()
    source_service = SourceService(source_port=source_repository)
    picker_service = PickerService(pickers_port=picker_repository)
    filter_service = FilterService(filters_port=filter_repository)
    extractor_service = ExtractorService(extractor_port=wallabag_service)
    feed_service = FeedService(feeds_port=feed_repository, extractor_service=extractor_service)
    job_service = JobService(
        feed_service=feed_service,
        source_service=source_service,
        picker_service=picker_service,
        filter_service=filter_service,
        scheduler=scheduler_adapter,
        extractor_service=extractor_service,
        feeds_port=feed_repository
    )
    app.state.job_service = job_service
    scheduler_adapter.start()
    job_service.load_all()


@app.on_event("shutdown")
def shutdown():
    scheduler_adapter.shutdown()


@app.get(
    "/",
    summary="Welcome",
    description="Return a welcome message for the API.",
    response_model=WelcomeResponse,
    tags=["General"]
)
def welcome(request: Request):
    message_collection = WelcomeResponse()
    return message_collection

# Include all v1 routes
app.include_router(v1_router)
