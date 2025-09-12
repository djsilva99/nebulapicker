from fastapi import Depends
from sqlalchemy.orm import Session

from src.adapters.repositories.job_repository import JobRepository
from src.adapters.repositories.sources_repository import SourcesRepository
from src.configs.database import get_db


def get_sources_repository(db: Session = Depends(get_db)) -> SourcesRepository: # noqa: B008
    """
    Provides the concrete SourceRepository implementation as a dependency.
    """
    return SourcesRepository(db)

def get_job_repository(db: Session = Depends(get_db)) -> JobRepository:
    return JobRepository(db)
