from fastapi import Depends
from sqlalchemy.orm import Session
from src.adapters.repositories.source_repository import SourceRepository
from src.configs.database import get_db


def get_source_repository(db: Session = Depends(get_db)) -> SourceRepository: # noqa: B008
    """
    Provides the concrete SourceRepository implementation as a dependency.
    """
    return SourceRepository(db)
