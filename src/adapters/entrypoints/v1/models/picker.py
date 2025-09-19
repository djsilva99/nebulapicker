from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator
from src.adapters.entrypoints.v1.exceptions import NoFiltersError
from src.adapters.entrypoints.v1.models.filter import FilterItem


class CreateFullPickerRequest(BaseModel):
    cronjob: str
    source_url: str
    filters: list[FilterItem]
    feed_external_id: UUID | None = None
    feed_name: str | None = None

    @model_validator(mode="after")
    def check_filters_not_empty(self):
        if len(self.filters) < 1:
            raise NoFiltersError(type(self), self.filters)
        return self


class FullPickerResponse(BaseModel):
    cronjob: str
    source_url: str
    filters: list[FilterItem]
    feed_external_id: UUID
    external_id: UUID
    created_at: datetime


class FullFeedPickerResponse(BaseModel):
    cronjob: str
    source_url: str
    filters: list[FilterItem]
    external_id: UUID
    created_at: datetime
