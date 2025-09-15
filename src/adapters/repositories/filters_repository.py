from sqlalchemy import text
from sqlalchemy.orm import Session
from src.domain.models.filter import Filter, FilterRequest
from src.domain.ports.filters_port import FiltersPort


class FiltersRepository(FiltersPort):

    def __init__(self, db: Session):
        self.db = db

    def create(self, filter_request: FilterRequest) -> Filter:
        sql = text(
            "INSERT INTO filters (picker_id, operation, args) "
            "VALUES (:picker_id, :operation, :args) "
            "RETURNING id, picker_id, operation, args, created_at"
        )
        result = self.db.execute(
            sql,
            {
                "picker_id": filter_request.picker_id,
                "operation": filter_request.operation,
                "args": filter_request.args
            }
        ).first()

        self.db.commit()

        data = result._mapping
        return Filter(
            id=data["id"],
            picker_id=data["picker_id"],
            operation=data["operation"],
            args=data["args"],
            created_at=data["created_at"],
        )

    def get_by_picker_id(self, picker_id: int) -> list[Filter]:
        sql = text(
            "SELECT id, picker_id, operation, args, created_at "
            "FROM filters WHERE picker_id = :picker_id;"
        )
        result = self.db.execute(sql, {"picker_id": picker_id})

        return [
            Filter(**item._mapping) for item in result
        ]
