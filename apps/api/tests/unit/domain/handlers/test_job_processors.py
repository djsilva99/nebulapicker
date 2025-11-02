from unittest.mock import MagicMock

from src.domain.handlers.job_processors import process_filters
from src.domain.services.job_service import JobService


def test_process_filters_calls_job_service_with_int():
    # GIVEN
    mock_job_service = MagicMock(spec=JobService)
    picker_id = "123"

    # WHEN
    process_filters(picker_id, mock_job_service)

    # THEN
    mock_job_service.process.assert_called_once_with(123)
