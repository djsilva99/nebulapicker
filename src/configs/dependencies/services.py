from fastapi import Depends, Request
from src.adapters.repositories.feeds_repository import FeedsRepository
from src.adapters.repositories.sources_repository import SourcesRepository
from src.configs.dependencies.repositories import get_feeds_repository, get_sources_repository
from src.domain.services.feed_service import FeedService
from src.domain.services.job_service import JobService
from src.domain.services.source_service import SourceService


def get_source_service(
    repository: SourcesRepository = Depends(get_sources_repository) # noqa: B008
) -> SourceService:
    return SourceService(source_port=repository)


def get_feed_service(
    repository: FeedsRepository = Depends(get_feeds_repository)  # noqa: B008
) -> FeedService:
    return FeedService(feeds_port=repository)


def get_job_service(request: Request) -> JobService:
    return request.app.state.job_service
