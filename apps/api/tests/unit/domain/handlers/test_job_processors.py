from unittest.mock import MagicMock, patch

from src.domain.handlers.job_processors import process_filters


@patch("src.main.app")
def test_process_filters_calls_job_service_with_int(mock_app):
    # GIVEN
    mock_job_service = MagicMock()
    mock_app.state.job_service = mock_job_service

    picker_id = "123"

    # WHEN
    process_filters(picker_id)

    # THEN
    mock_job_service.process.assert_called_once_with(123)
