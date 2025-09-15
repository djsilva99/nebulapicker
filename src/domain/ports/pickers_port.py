from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.models.picker import Picker, PickerRequest


class PickersPort(ABC):

    @abstractmethod
    def create(self, picker_request: PickerRequest) -> Picker:
        pass

    @abstractmethod
    def delete(self, picker_id: int) -> bool:
        pass

    @abstractmethod
    def get_by_external_id(self, external_id: UUID) -> Picker | None:
        pass
