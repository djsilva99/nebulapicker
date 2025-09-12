from sqlalchemy import text
from sqlalchemy.orm import Session
from src.domain.models.source import Source
from src.domain.ports.source_port import SourcePort


class SourcesRepository(SourcePort):
    """
    Implementation of the Source repository port.
    This class handles the database logic using raw SQL.
    """

    def __init__(self, db: Session):
        """
        Initializes the repository with a database session.
        """
        self.db = db

    def get_by_id(self, source_id: int) -> Source | None:
        """
        Retrieves a source by its ID.
        """
        sql = text("SELECT id, external_id, url, name, created_at FROM sources WHERE id = :id")
        result = self.db.execute(sql, {"id": source_id}).first()

        if result:
            return Source(**result._mapping)
        return None

    def get_all(self) -> list[Source]:
        """
        Retrieves all sources.
        """
        sql = text("SELECT id, external_id, url, name, created_at FROM sources")
        result = self.db.execute(sql)

        if result:
            return [
                Source(**item._mapping) for item in result
            ]
        return []
