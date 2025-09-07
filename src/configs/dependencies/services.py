from fastapi import Depends
from src.adapters.repositories.source_repository import SourceRepository
from src.configs.dependencies.repositories import get_source_repository
from src.domain.services.source_service import SourceService


def get_source_service(
    repository: SourceRepository = Depends(get_source_repository) # noqa: B008
) -> SourceService:
    """
    Provides the SourceService by injecting the SourceRepository.
    """
    return SourceService(source_port=repository)
