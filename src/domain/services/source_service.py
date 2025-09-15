from uuid import UUID

from src.domain.models.source import Source, SourceRequest
from src.domain.ports.sources_port import SourcePort


class SourceService:
    def __init__(self, source_port: SourcePort):
        self.source_port = source_port

    def create_source(self, source_request: SourceRequest) -> Source:
        return self.source_port.create(source_request)

    def get_all_sources(self) -> list[Source]:
        return self.source_port.get_all()

    def get_source_by_external_id(self, external_id: UUID):
        return self.source_port.get_by_external_id(external_id)

    def get_source_by_url(self, url: str):
        return self.source_port.get_by_url(url)
