from uuid import UUID

from pydantic import BaseModel
from src.domain.models.source import Source


class SourceItem(BaseModel):
    external_id: UUID
    url: str
    name: str


class GetAllSourcesResponse(BaseModel):
    sources: list[SourceItem] | None


class CreateSourceRequest(BaseModel):
    url: str
    name: str


class CreateSourceResponse(BaseModel):
    external_id: UUID
    url: str
    name: str


def map_source_list_to_get_all_sources_response(
    source_list: list[Source]
) -> list[SourceItem]:
    return [
        SourceItem(
            external_id=source.external_id,
            url=source.url,
            name=source.name,
        )
        for source in source_list
    ]


def map_source_to_create_source_response(
    source: Source
) -> CreateSourceResponse:
    return CreateSourceResponse(
        external_id=source.external_id,
        url=source.url,
        name=source.name
    )
