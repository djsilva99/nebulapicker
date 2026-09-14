from src.adapters.repositories.feeds_repository import FeedsRepository
from src.adapters.repositories.filters_repository import FiltersRepository
from src.adapters.repositories.pickers_repository import PickersRepository
from src.adapters.repositories.sources_repository import SourcesRepository
from src.adapters.wallabag_extractor import WallabagExtractor
from src.celery_app import celery_app
from src.configs.database import SessionLocal
from src.domain.services.extractor_service import ExtractorService
from src.domain.services.feed_service import FeedService
from src.domain.services.filter_service import FilterService
from src.domain.services.job_service import JobService
from src.domain.services.picker_service import PickerService
from src.domain.services.source_service import SourceService


@celery_app.task
def process_picker(picker_id: int):
    feed_repository = FeedsRepository(SessionLocal)
    source_repository = SourcesRepository(SessionLocal)
    picker_repository = PickersRepository(SessionLocal)
    filter_repository = FiltersRepository(SessionLocal)

    wallabag_service = WallabagExtractor()

    source_service = SourceService(
        source_port=source_repository,
    )

    picker_service = PickerService(
        pickers_port=picker_repository,
    )

    filter_service = FilterService(
        filters_port=filter_repository,
    )

    extractor_service = ExtractorService(
        extractor_port=wallabag_service,
    )

    feed_service = FeedService(
        feeds_port=feed_repository,
        extractor_service=extractor_service,
    )

    job_service = JobService(
        scheduler=None,
        picker_service=picker_service,
        filter_service=filter_service,
        source_service=source_service,
        feed_service=feed_service,
        extractor_service=extractor_service,
        feeds_port=feed_repository,
    )

    return job_service.process(picker_id)
