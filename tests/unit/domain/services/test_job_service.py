import pytest
from unittest.mock import MagicMock
from datetime import datetime

from src.domain.models.job import JobRequest, Job
from src.domain.services.job_service import JobService  # adjust import if needed


@pytest.fixture
def scheduler_mock():
    return MagicMock()


@pytest.fixture
def job_port_mock():
    return MagicMock()


@pytest.fixture
def job_service(scheduler_mock, job_port_mock):
    return JobService(scheduler=scheduler_mock, job_port=job_port_mock)


def test_add_cronjob_calls_ports(job_service, scheduler_mock, job_port_mock):
    # GIVEN
    job_request = JobRequest(
        func_name="test_func",
        args=["a1", "a2"],
        schedule="* * * * *"
    )

    # WHEN
    job_service.add_cronjob(job_request)

    # THEN
    job_port_mock.create.assert_called_once_with(job_request)


def test_load_all_fetches_jobs_and_loads(job_service, scheduler_mock, job_port_mock):
    # GIVEN
    jobs = [
        Job(
            id=1,
            func_name="func1",
            args=["a"],
            schedule="* * * * *",
            created_at=datetime(2025, 1, 1, 12, 0, 0)
        ),
        Job(
            id=2,
            func_name="func2",
            args=["b"],
            schedule="0 0 * * *",
            created_at=datetime(2025, 1, 1, 13, 0, 0)
        ),
    ]
    job_port_mock.get_all.return_value = jobs

    # WHEN
    job_service.load_all()

    # THEN
    job_port_mock.get_all.assert_called_once()
    scheduler_mock.load_jobs.assert_called_once_with(jobs)
