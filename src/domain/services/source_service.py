from src.domain.models.source import Source
from src.domain.ports.source_port import SourcePort


class SourceService:
    def __init__(self, source_port: SourcePort):
        self.source_port = source_port

    def get_all_sources(self) -> list[Source]:
        """
        Returns a list of all sources.
        """
        return self.source_port.get_all()
