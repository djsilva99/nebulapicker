from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from src.domain.models.picker import Picker, PickerRequest
from src.domain.services.picker_service import PickerService


@pytest.fixture
def pickers_port_mock():
    return MagicMock()


@pytest.fixture
def picker_service(pickers_port_mock):
    return PickerService(pickers_port=pickers_port_mock)


def test_create_picker(picker_service, pickers_port_mock):
    # GIVEN
    external_id = uuid4()
    picker_request = PickerRequest(
        source_id=1,
        feed_id=1,
        cronjob="30 * * * *"
    )
    expected_picker = Picker(
        id=1,
        external_id=external_id,
        source_id=1,
        feed_id=1,
        cronjob="30 * * * *",
        created_at=datetime(2025, 1, 1, 12, 0, 0),
    )
    pickers_port_mock.create.return_value = expected_picker

    # WHEN
    created_picker = picker_service.create_picker(picker_request)

    # THEN
    pickers_port_mock.create.assert_called_once_with(picker_request)
    assert created_picker is not None
    assert created_picker.external_id == external_id
    assert created_picker.source_id == 1
    assert created_picker.feed_id == 1
    assert created_picker.cronjob == "30 * * * *"


def test_get_pickers_by_external_id_success(picker_service, pickers_port_mock):
    # GIVEN
    external_id = uuid4()
    picker = Picker(
        id=1,
        external_id=external_id,
        source_id=1,
        feed_id=1,
        cronjob="30 * * * *",
        created_at=datetime(2025, 1, 1, 12, 0, 0),
    )
    pickers_port_mock.get_by_external_id.return_value = picker

    # WHEN
    picker_response = picker_service.get_picker_by_external_id(external_id)

    # THEN
    pickers_port_mock.get_by_external_id.assert_called_once()
    assert picker_response == picker


def test_get_filters_by_picker_id_returns_none(picker_service, pickers_port_mock):
    # GIVEN
    pickers_port_mock.get_by_external_id.return_value = None

    # WHEN
    picker_response = picker_service.get_picker_by_external_id(uuid4())

    # THEN
    pickers_port_mock.get_by_external_id.assert_called_once()
    assert picker_response is None


def test_delete_picker_success(picker_service, pickers_port_mock):
    # GIVEN
    pickers_port_mock.delete.return_value = True

    # WHEN
    result = picker_service.delete_picker(123)

    # THEN
    pickers_port_mock.delete.assert_called_once_with(123)
    assert result is True


def test_delete_filter_not_found(picker_service, pickers_port_mock):
    # GIVEN
    pickers_port_mock.delete.return_value = False

    # WHEN
    result = picker_service.delete_picker(999)

    # THEN
    pickers_port_mock.delete.assert_called_once_with(999)
    assert result is False
