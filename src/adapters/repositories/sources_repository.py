from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session
from src.domain.models.source import Source, SourceRequest
from src.domain.ports.sources_port import SourcePort


class SourcesRepository(SourcePort):

    def __init__(self, db: Session):
        self.db = db

    def create(self, source_request: SourceRequest) -> Source:
        sql = text(
            "INSERT INTO sources (url, name) "
            "VALUES (:url, :name) "
            "RETURNING id, external_id, url, name, created_at"
        )
        result = self.db.execute(
            sql,
            {
                "url": source_request.url,
                "name": source_request.name
            }
        ).mappings().first()

        self.db.commit()

        return Source(
            id=result["id"],
            external_id=result["external_id"],
            url=result["url"],
            name=result["name"],
            created_at=result["created_at"],
        )

    def get_all(self) -> list[Source]:
        sql = text("SELECT id, external_id, url, name, created_at FROM sources")
        result = self.db.execute(sql)

        if result:
            return [
                Source(**item._mapping) for item in result
            ]
        return []

    def get_by_external_id(self, external_id: UUID) -> Source | None:
        sql = text(
            "SELECT id, external_id, url, name, created_at "
            "FROM sources WHERE external_id = :external_id;"
        )
        result = self.db.execute(sql, {"external_id": str(external_id)}).mappings().first()

        if result:
            return Source(**result)
        return None

    def get_by_url(self, url: str) -> Source | None:
        sql = text(
            "SELECT id, external_id, url, name, created_at "
            "FROM sources WHERE url = :url;"
        )
        result = self.db.execute(sql, {"url": url}).mappings().first()

        if result is None:
            return None

        return Source(
            id=result["id"],
            external_id=result["external_id"],
            url=result["url"],
            name=result["name"],
            created_at=result["created_at"],
        )
