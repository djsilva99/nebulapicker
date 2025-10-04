from uuid import UUID

from src.domain.models.picker import Picker, PickerRequest
from src.domain.ports.pickers_port import PickersPort


class PickerService:
    def __init__(self, pickers_port: PickersPort):
        self.pickers_port = pickers_port

    def create_picker(self, picker_request: PickerRequest) -> Picker:
        return self.pickers_port.create_picker(picker_request)

    def delete_picker(self, picker_id: int) -> bool:
        return self.pickers_port.delete_picker(picker_id)

    def get_picker_by_external_id(self, external_id: UUID) -> Picker:
        return self.pickers_port.get_picker_by_external_id(external_id)

    def get_picker_by_id(self, picker_id: int) -> Picker:
        return self.pickers_port.get_picker_by_id(picker_id)

    def get_pickers_by_feed_id(self, feed_id: int) -> list[Picker]:
        return self.pickers_port.get_pickers_by_feed_id(feed_id)

    def get_all_pickers(self) -> list[Picker]:
        return self.pickers_port.get_all_pickers()

    def get_pickers_by_source_id(self, source_id: int) -> list[Picker]:
        return self.pickers_port.get_picker_by_source_id(source_id)
