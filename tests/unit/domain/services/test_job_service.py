from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from src.domain.models.feed import FeedItemRequest
from src.domain.models.filter import Operation
from src.domain.models.job import Job
from src.domain.models.picker import Picker
from src.domain.services.job_service import JobService


@pytest.fixture
def mock_services():
    return {
        "scheduler": MagicMock(),
        "picker_service": MagicMock(),
        "filter_service": MagicMock(),
        "source_service": MagicMock(),
        "feed_service": MagicMock(),
    }


@pytest.fixture
def job_service(mock_services):
    return JobService(
        scheduler=mock_services["scheduler"],
        picker_service=mock_services["picker_service"],
        filter_service=mock_services["filter_service"],
        source_service=mock_services["source_service"],
        feed_service=mock_services["feed_service"],
    )


def test_add_cronjob(job_service, mock_services):
    picker = Picker(
        id=1,
        cronjob="*/5 * * * *",
        source_id=1,
        feed_id=1,
        external_id=uuid4(),
        created_at=datetime(2025, 1, 1, 13, 0, 0)
    )

    job_service.add_cronjob(picker)

    # Assert scheduler.add_job was called with a Job
    assert mock_services["scheduler"].add_job.call_count == 1
    job_arg = mock_services["scheduler"].add_job.call_args[0][0]
    assert isinstance(job_arg, Job)
    assert job_arg.func_name == "process_filters"
    assert str(picker.id) in job_arg.args


def test_load_all(job_service, mock_services):
    picker1 = Picker(
        id=1,
        cronjob="*/5 * * * *",
        source_id=1,
        feed_id=1,
        external_id=uuid4(),
        created_at=datetime(2025, 1, 1, 12, 0, 0)
    )
    picker2 = Picker(
        id=2,
        cronjob="*/10 * * * *",
        source_id=2,
        feed_id=2,
        external_id=uuid4(),
        created_at=datetime(2025, 1, 1, 13, 0, 0)
    )
    mock_services["picker_service"].get_all_pickers.return_value = [picker1, picker2]

    job_service.load_all()

    jobs_arg = mock_services["scheduler"].load_jobs.call_args[0][0]
    assert len(jobs_arg) == 2
    assert all(isinstance(job, Job) for job in jobs_arg)


@patch("src.domain.services.job_service.feedparser.parse")
def test_process_adds_new_entry(mock_parse, job_service, mock_services):
    # Picker and dependencies
    picker = Picker(
        id=1,
        cronjob="*/5 * * * *",
        source_id=10,
        feed_id=20,
        external_id=uuid4(),
        created_at=datetime(2025, 1, 1, 13, 0, 0)
    )
    mock_services["picker_service"].get_picker_by_id.return_value = picker
    mock_services["filter_service"].get_filters_by_picker_id.return_value = [
        MagicMock(operation=Operation.identity)
    ]
    mock_services["feed_service"].get_feed_items.return_value = []
    mock_services["source_service"].get_source_by_id.return_value = MagicMock(
        url="http://example.com/feed"
    )

    # Mock feedparser returning one entry
    mock_parse.return_value.entries = [
        MagicMock(link="http://example.com/article1", title="Article 1", description="Desc 1")
    ]

    job_service.process(picker_id=1)

    # Assert a feed item was created
    assert mock_services["feed_service"].create_feed_item.call_count == 1
    feed_item = mock_services["feed_service"].create_feed_item.call_args[0][0]
    assert isinstance(feed_item, FeedItemRequest)
    assert feed_item.link == "http://example.com/article1"
    assert feed_item.feed_id == picker.feed_id


@patch("src.domain.services.job_service.feedparser.parse")
def test_process_skips_existing_entry(mock_parse, job_service, mock_services):
    picker = Picker(
        id=1,
        cronjob="*/5 * * * *",
        source_id=10,
        feed_id=20,
        external_id=uuid4(),
        created_at=datetime(2025, 1, 1, 13, 0, 0)
    )
    mock_services["picker_service"].get_picker_by_id.return_value = picker
    mock_services["filter_service"].get_filters_by_picker_id.return_value = []
    mock_services["feed_service"].get_feed_items.return_value = [
        MagicMock(link="http://example.com/article1")
    ]
    mock_services["source_service"].get_source_by_id.return_value = MagicMock(
        url="http://example.com/feed"
    )

    mock_parse.return_value.entries = [
        MagicMock(link="http://example.com/article1", title="Article 1", description="Desc 1")
    ]

    job_service.process(picker_id=1)

    # Should not create new feed item
    mock_services["feed_service"].create_feed_item.assert_not_called()


@patch("src.domain.services.job_service.feedparser.parse")
def test_process_with_identity_filter_false(mock_parse, job_service, mock_services):
    picker = Picker(
        id=1,
        cronjob="*/5 * * * *",
        source_id=10,
        feed_id=20,
        external_id=uuid4(),
        created_at=datetime(2025, 1, 1, 13, 0, 0)
    )
    mock_services["picker_service"].get_picker_by_id.return_value = picker
    # Returning an "identity" filter ensures identity() gets called
    mock_services["filter_service"].get_filters_by_picker_id.return_value = [
        MagicMock(operation=Operation.identity)
    ]
    mock_services["feed_service"].get_feed_items.return_value = []
    mock_services["source_service"].get_source_by_id.return_value = MagicMock(
        url="http://example.com/feed"
    )

    mock_parse.return_value.entries = [
        MagicMock(link="http://example.com/article2", title="Article 2", description="Desc 2")
    ]

    job_service.process(picker_id=1)

    # Since identity just returns True unchanged, item is created
    mock_services["feed_service"].create_feed_item.assert_called_once()
