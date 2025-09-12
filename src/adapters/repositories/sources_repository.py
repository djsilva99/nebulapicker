from sqlalchemy import text
from sqlalchemy.orm import Session
from src.domain.models.source import Source
from src.domain.ports.sources_port import SourcePort


class SourcesRepository(SourcePort):

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, source_id: int) -> Source | None:
        sql = text("SELECT id, external_id, url, name, created_at FROM sources WHERE id = :id")
        result = self.db.execute(sql, {"id": source_id}).first()

        if result:
            return Source(**result._mapping)
        return None

    def get_all(self) -> list[Source]:
        sql = text("SELECT id, external_id, url, name, created_at FROM sources")
        result = self.db.execute(sql)

        if result:
            return [
                Source(**item._mapping) for item in result
            ]
        return []
