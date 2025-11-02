from uuid import UUID

from src.domain.models.source import Source, SourceRequest
from src.domain.ports.sources_port import SourcePort


class SourceService:
    def __init__(self, source_port: SourcePort):
        self.source_port = source_port

    def create_source(self, source_request: SourceRequest) -> Source:
        return self.source_port.create_source(source_request)

    def update_source(
        self,
        source_external_id,
        source_request: SourceRequest
    ) -> Source | None:
        source = self.get_source_by_external_id(source_external_id)
        if source is None:
            return None
        return self.source_port.update_source(source.id, source_request)

    def delete_source(self, source_id: int) -> bool:
        return self.source_port.delete_source(source_id)

    def get_all_sources(self) -> list[Source]:
        return self.source_port.get_all_sources()

    def get_source_by_external_id(self, external_id: UUID):
        return self.source_port.get_source_by_external_id(external_id)

    def get_source_by_id(self, id: int):
        return self.source_port.get_source_by_id(id)

    def get_source_by_url(self, url: str):
        return self.source_port.get_source_by_url(url)
