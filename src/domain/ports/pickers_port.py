from abc import ABC, abstractmethod
from uuid import UUID

from src.domain.models.picker import Picker, PickerRequest


class PickersPort(ABC):

    @abstractmethod
    def create_picker(self, picker_request: PickerRequest) -> Picker:
        pass

    @abstractmethod
    def delete_picker(self, picker_id: int) -> bool:
        pass

    @abstractmethod
    def get_picker_by_external_id(self, external_id: UUID) -> Picker | None:
        pass

    @abstractmethod
    def get_picker_by_id(self, picker_id: int) -> Picker | None:
        pass

    @abstractmethod
    def get_all_pickers(self) -> list[Picker]:
        pass

    @abstractmethod
    def get_pickers_by_feed_id(self, feed_id: int) -> list[Picker]:
        pass
