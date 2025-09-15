from fastapi import Depends
from sqlalchemy.orm import Session
from src.adapters.repositories.feeds_repository import FeedsRepository
from src.adapters.repositories.filters_repository import FiltersRepository
from src.adapters.repositories.jobs_repository import JobRepository
from src.adapters.repositories.pickers_repository import PickersRepository
from src.adapters.repositories.sources_repository import SourcesRepository
from src.configs.database import get_db


def get_sources_repository(db: Session = Depends(get_db)) -> SourcesRepository: # noqa: B008
    return SourcesRepository(db)

def get_feeds_repository(db: Session = Depends(get_db)) -> FeedsRepository: # noqa: B008
    return FeedsRepository(db)

def get_job_repository(db: Session = Depends(get_db)) -> JobRepository: # noqa: B008
    return JobRepository(db)

def get_filters_repository(db: Session = Depends(get_db)) -> FiltersRepository: # noqa: B008
    return FiltersRepository(db)

def get_pickers_repository(db: Session = Depends(get_db)) -> PickersRepository: # noqa: B008
    return PickersRepository(db)
