import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.domain.models.job import Job
from src.adapters.scheduler import Scheduler


@pytest.fixture
def mock_scheduler():
    # Patch the BackgroundScheduler symbol inside scheduler.py
    with patch("src.adapters.scheduler.BackgroundScheduler") as MockScheduler:
        mock_instance = MagicMock()
        MockScheduler.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def scheduler(mock_scheduler):
    return Scheduler()


def test_start_calls_scheduler_start(scheduler, mock_scheduler):
    scheduler.start()
    mock_scheduler.start.assert_called_once()


def test_shutdown_calls_scheduler_shutdown(scheduler, mock_scheduler):
    scheduler.shutdown()
    mock_scheduler.shutdown.assert_called_once()


def test_add_job_calls_scheduler_add_job(scheduler, mock_scheduler):
    # GIVEN
    job = Job(
        id=1,
        func_name="test_func",
        args=["arg1", "arg2"],
        schedule="* * * * *",
        created_at=datetime(2025, 1, 1, 13, 0, 0)
    )
    # Patch FUNCTIONS to include our fake function
    with patch("src.adapters.scheduler.FUNCTIONS", {"test_func": MagicMock()}) as mock_funcs:
        # WHEN
        scheduler.add_job(job)

        # THEN
        mock_scheduler.add_job.assert_called_once()
        called_kwargs = mock_scheduler.add_job.call_args.kwargs

        assert called_kwargs["func"] == mock_funcs["test_func"]
        assert called_kwargs["args"] == job.args
        assert called_kwargs["trigger"].__class__.__name__ == "CronTrigger"


def test_add_job_unknown_function_does_not_schedule(scheduler, mock_scheduler, capsys):
    # GIVEN
    job = Job(
        id=2,
        func_name="does_not_exist",
        args=[],
        schedule="* * * * *",
        created_at=datetime(2025, 1, 1, 13, 0, 0)
    )

    # WHEN
    scheduler.add_job(job)

    # THEN
    mock_scheduler.add_job.assert_not_called()
    captured = capsys.readouterr()
    assert "Function does_not_exist not found" in captured.out


def test_load_jobs_calls_add_job_for_each(scheduler):
    # GIVEN
    jobs = [
        Job(
            id=1,
            func_name="f1",
            args=[],
            schedule="* * * * *",
            created_at=datetime(2025, 1, 1, 13, 0, 0)
        ),
        Job(
            id=2,
            func_name="f2",
            args=[],
            schedule="0 0 * * *",
            created_at=datetime(2025, 1, 1, 14, 0, 0)
        ),
    ]

    with patch.object(scheduler, "add_job") as mock_add_job:
        # WHEN
        scheduler.load_jobs(jobs)

        # THEN
        assert mock_add_job.call_count == 2
        mock_add_job.assert_any_call(jobs[0])
        mock_add_job.assert_any_call(jobs[1])
