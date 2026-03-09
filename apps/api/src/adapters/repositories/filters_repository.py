from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from src.domain.models.filter import Filter, FilterRequest
from src.domain.ports.filters_port import FiltersPort


class FiltersRepository(FiltersPort):

    def __init__(self, session_factory: sessionmaker):
        self.session_factory = session_factory

    def create_filter(self, filter_request: FilterRequest) -> Filter:
        sql = text(
            "INSERT INTO filters (picker_id, operation, args) "
            "VALUES (:picker_id, :operation, :args) "
            "RETURNING id, picker_id, operation, args, created_at"
        )
        with self.session_factory() as session:
            result = session.execute(
                sql,
                {
                    "picker_id": filter_request.picker_id,
                    "operation": filter_request.operation,
                    "args": filter_request.args
                }
            ).first()

            session.commit()

            data = result._mapping
            return Filter(
                id=data["id"],
                picker_id=data["picker_id"],
                operation=data["operation"],
                args=data["args"],
                created_at=data["created_at"],
            )

    def delete_filter(self, filter_id: int) -> bool:
        sql = text("DELETE FROM filters WHERE id = :id RETURNING id")
        with self.session_factory() as session:
            result = session.execute(sql, {"id": filter_id}).first()
            session.commit()
            return result is not None

    def get_filter_by_picker_id(self, picker_id: int) -> list[Filter]:
        sql = text(
            "SELECT id, picker_id, operation, args, created_at "
            "FROM filters WHERE picker_id = :picker_id;"
        )
        with self.session_factory() as session:
            result = session.execute(sql, {"picker_id": picker_id})
            # We convert to domain models before the session closes
            return [
                Filter(**item._mapping) for item in result
            ]
