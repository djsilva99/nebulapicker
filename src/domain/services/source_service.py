from src.domain.models.source import Source
from src.domain.ports.sources_port import SourcePort


class SourceService:
    def __init__(self, source_port: SourcePort):
        self.source_port = source_port

    def get_all_sources(self) -> list[Source]:
        return self.source_port.get_all()
