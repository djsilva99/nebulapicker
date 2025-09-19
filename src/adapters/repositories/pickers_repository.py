from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session
from src.domain.models.picker import Picker, PickerRequest
from src.domain.ports.pickers_port import PickersPort


class PickersRepository(PickersPort):

    def __init__(self, db: Session):
        self.db = db

    def create(self, picker_request: PickerRequest) -> Picker:
        sql = text(
            "INSERT INTO pickers (source_id, feed_id, cronjob) "
            "VALUES (:source_id, :feed_id, :cronjob) "
            "RETURNING id, external_id, source_id, feed_id, cronjob, created_at"
        )
        result = self.db.execute(
            sql,
            {
                "source_id": picker_request.source_id,
                "feed_id": picker_request.feed_id,
                "cronjob": picker_request.cronjob
            }
        ).first()

        self.db.commit()

        data = result._mapping
        return Picker(
            id=data["id"],
            external_id=data["external_id"],
            source_id=data["source_id"],
            feed_id=data["feed_id"],
            cronjob=data["cronjob"],
            created_at=data["created_at"],
        )

    def delete(self, picker_id: int) -> bool:
        sql = text("DELETE FROM pickers WHERE id = :id RETURNING id")
        result = self.db.execute(sql, {"id": picker_id}).first()
        self.db.commit()
        return result is not None

    def get_by_external_id(self, external_id: UUID) -> Picker | None:
        sql = text(
            "SELECT id, external_id, source_id, feed_id, cronjob, created_at "
            "FROM pickers WHERE external_id = :external_id;"
        )
        result = self.db.execute(sql, {"external_id": external_id}).mappings().first()

        if result:
            return Picker(**result)
        return None

    def get_pickers_by_feed_id(
        self,
        feed_id: int
    ) -> list[Picker]:
        sql = text(
            "SELECT id, external_id, source_id, feed_id, cronjob, created_at "
            "FROM pickers WHERE feed_id = :feed_id;"
        )
        result = self.db.execute(sql, {"feed_id": feed_id}).mappings()

        return [Picker(**picker) for picker in result]
