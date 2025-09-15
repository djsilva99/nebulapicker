from datetime import datetime
from unittest.mock import MagicMock

import pytest
from src.domain.models.filter import Filter, FilterRequest, Operation
from src.domain.services.filter_service import FilterService


@pytest.fixture
def filters_port_mock():
    return MagicMock()


@pytest.fixture
def filter_service(filters_port_mock):
    return FilterService(filters_port=filters_port_mock)


def test_create_filter(filter_service, filters_port_mock):
    # GIVEN
    filter_request = FilterRequest(
        picker_id=1,
        operation=Operation('identity'),
        args="[a]"
    )
    expected_filter = Filter(
        id=1,
        picker_id=1,
        operation=Operation('identity'),
        args="[a]",
        created_at=datetime(2025, 1, 1, 12, 0, 0),
    )
    filters_port_mock.create.return_value = expected_filter

    # WHEN
    created_filter = filter_service.create_filter(filter_request)

    # THEN
    filters_port_mock.create.assert_called_once_with(filter_request)
    assert created_filter is not None
    assert created_filter.picker_id == 1
    assert created_filter.operation == Operation('identity')
    assert created_filter.args == "[a]"


def test_get_filters_by_picker_id_success(filter_service, filters_port_mock):
    # GIVEN
    filters = [
        Filter(
            id=1,
            picker_id=1,
            operation=Operation('identity'),
            args="[a]",
            created_at=datetime(2025, 1, 1, 12, 0, 0)
        ),
        Filter(
            id=2,
            picker_id=1,
            operation=Operation('identity'),
            args="[b]",
            created_at=datetime(2025, 1, 1, 13, 0, 0)
        ),
    ]
    filters_port_mock.get_by_picker_id.return_value = filters

    # WHEN
    all_filters = filter_service.get_filters_by_picker_id(1)

    # THEN
    filters_port_mock.get_by_picker_id.assert_called_once()
    assert all_filters == filters


def test_get_filters_by_picker_id_returns_empty(filter_service, filters_port_mock):
    # GIVEN
    filters = []
    filters_port_mock.get_by_picker_id.return_value = filters

    # WHEN
    all_filters = filter_service.get_filters_by_picker_id(1)

    # THEN
    filters_port_mock.get_by_picker_id.assert_called_once()
    assert all_filters == filters
