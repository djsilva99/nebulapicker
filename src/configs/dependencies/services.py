from fastapi import Depends, Request
from src.adapters.repositories.sources_repository import SourcesRepository
from src.configs.dependencies.repositories import get_sources_repository
from src.domain.services.job_service import JobService
from src.domain.services.source_service import SourceService


def get_source_service(
    repository: SourcesRepository = Depends(get_sources_repository) # noqa: B008
) -> SourceService:
    """
    Provides the SourceService by injecting the SourceRepository.
    """
    return SourceService(source_port=repository)


def get_job_service(request: Request) -> JobService:
    return request.app.state.job_service
