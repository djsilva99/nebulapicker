from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from src.domain.models.feed import FeedItemRequest
from src.domain.models.filter import Operation
from src.domain.models.job import Job
from src.domain.models.picker import Picker
from src.domain.services.job_service import JobService, settings

settings.WALLABAG_ENABLED = False


class AttrDict(dict):
    def __getattr__(self, item):
        return self.get(item)


@pytest.fixture
def mock_services():
    return {
        "scheduler": MagicMock(),
        "picker_service": MagicMock(),
        "filter_service": MagicMock(),
        "source_service": MagicMock(),
        "feed_service": MagicMock(),
        "extractor_service": MagicMock(),
    }


@pytest.fixture
def job_service(mock_services):
    return JobService(
        scheduler=mock_services["scheduler"],
        picker_service=mock_services["picker_service"],
        filter_service=mock_services["filter_service"],
        source_service=mock_services["source_service"],
        feed_service=mock_services["feed_service"],
        extractor_service=mock_services["extractor_service"]
    )


def test_add_cronjob(job_service, mock_services):
    # GIVEN
    picker = Picker(
        id=1,
        cronjob="*/5 * * * *",
        source_id=1,
        feed_id=1,
        external_id=uuid4(),
        created_at=datetime(2025, 1, 1, 13, 0, 0)
    )

    # WHEN
    job_service.add_cronjob(picker)

    # THEN
    assert mock_services["scheduler"].add_job.call_count == 1
    job_arg = mock_services["scheduler"].add_job.call_args[0][0]
    assert isinstance(job_arg, Job)
    assert job_arg.func_name == "process_filters"
    assert str(picker.id) in job_arg.args


def test_load_all(job_service, mock_services):
    # GIVEN
    picker1 = Picker(
        id=1, cronjob="*/5 * * * *", source_id=1, feed_id=1, external_id=uuid4(),
        created_at=datetime(2025, 1, 1, 12, 0, 0)
    )
    picker2 = Picker(
        id=2, cronjob="*/10 * * * *", source_id=2, feed_id=2, external_id=uuid4(),
        created_at=datetime(2025, 1, 1, 13, 0, 0)
    )
    mock_services["picker_service"].get_all_pickers.return_value = [picker1, picker2]

    # WHEN
    job_service.load_all()

    # THEN
    jobs_arg = mock_services["scheduler"].load_jobs.call_args[0][0]
    assert len(jobs_arg) == 2
    assert all(isinstance(job, Job) for job in jobs_arg)


@patch("src.domain.services.job_service.feedparser.parse")
def test_process_adds_new_entry(mock_parse, job_service, mock_services):
    # GIVEN
    picker = Picker(
        id=1, cronjob="*/5 * * * *", source_id=10, feed_id=20,
        external_id=uuid4(), created_at=datetime(2025, 1, 1, 13, 0, 0)
    )
    mock_services["picker_service"].get_picker_by_id.return_value = picker
    filter_mock = MagicMock(operation=Operation.identity)
    filter_mock.args = "[]"
    mock_services["filter_service"].get_filters_by_picker_id.return_value = [filter_mock]
    mock_services["feed_service"].get_feed_items.return_value = []
    mock_services["source_service"].get_source_by_id.return_value = SimpleNamespace(
        url="http://example.com/feed", name="Example Source"
    )

    mock_parse.return_value.entries = [
        AttrDict(
            link="http://example.com/article1",
            title="Article 1",
            description="Desc 1",
            content="test_content"
        )
    ]

    # WHEN
    job_service.process(picker_id=1)

    # THEN
    assert mock_services["feed_service"].create_feed_item.call_count == 1
    feed_item = mock_services["feed_service"].create_feed_item.call_args[0][0]
    assert isinstance(feed_item, FeedItemRequest)
    assert feed_item.link == "http://example.com/article1"
    assert feed_item.feed_id == picker.feed_id
    assert feed_item.author == "Example Source"


@patch("src.domain.services.job_service.feedparser.parse")
def test_process_skips_existing_entry(mock_parse, job_service, mock_services):
    # GIVEN
    picker = Picker(
        id=1, cronjob="*/5 * * * *", source_id=10, feed_id=20,
        external_id=uuid4(), created_at=datetime(2025, 1, 1, 13, 0, 0)
    )
    mock_services["picker_service"].get_picker_by_id.return_value = picker
    mock_services["filter_service"].get_filters_by_picker_id.return_value = []
    mock_services["feed_service"].get_feed_items.return_value = [
        SimpleNamespace(link="http://example.com/article1")
    ]
    mock_services["source_service"].get_source_by_id.return_value = SimpleNamespace(
        url="http://example.com/feed", name="Example Source"
    )

    mock_parse.return_value.entries = [
        SimpleNamespace(
            link="http://example.com/article1",
            title="Article 1",
            description="Desc 1"
        )
    ]

    # WHEN
    job_service.process(picker_id=1)

    # THEN
    mock_services["feed_service"].create_feed_item.assert_not_called()


@patch("src.domain.services.job_service.feedparser.parse")
def test_process_with_identity_filter(mock_parse, job_service, mock_services):
    # GIVEN
    picker = Picker(
        id=1, cronjob="*/5 * * * *", source_id=10, feed_id=20,
        external_id=uuid4(), created_at=datetime(2025, 1, 1, 13, 0, 0)
    )
    mock_services["picker_service"].get_picker_by_id.return_value = picker
    filter_mock = MagicMock(operation=Operation.identity)
    filter_mock.args = "[]"
    mock_services["filter_service"].get_filters_by_picker_id.return_value = [filter_mock]
    mock_services["feed_service"].get_feed_items.return_value = []
    mock_services["source_service"].get_source_by_id.return_value = AttrDict(
        url="http://example.com/feed", name="Example Source"
    )

    mock_parse.return_value.entries = [
        AttrDict(
            link="http://example.com/article2",
            title="Article 2",
            description="Desc 2"
        )
    ]

    # WHEN
    job_service.process(picker_id=1)

    # THEN
    mock_services["feed_service"].create_feed_item.assert_called_once()


@patch("src.domain.services.job_service.feedparser.parse")
def test_process_with_title_contains_filter(mock_parse, job_service, mock_services):
    # GIVEN
    picker = Picker(
        id=1, cronjob="*/5 * * * *", source_id=10, feed_id=20,
        external_id=uuid4(), created_at=datetime(2025, 1, 1, 13, 0, 0)
    )
    mock_services["picker_service"].get_picker_by_id.return_value = picker
    filter_mock = MagicMock(operation=Operation.title_contains, args="['Article', 1]")
    mock_services["filter_service"].get_filters_by_picker_id.return_value = [filter_mock]
    mock_services["feed_service"].get_feed_items.return_value = []
    mock_services["source_service"].get_source_by_id.return_value = AttrDict(
        url="http://example.com/feed", name="Example Source"
    )

    mock_parse.return_value.entries = [
        AttrDict(
            link="http://example.com/article",
            title="Article 123",
            description="Some text"
        )
    ]

    # WHEN
    job_service.process(picker_id=1)

    # THEN
    mock_services["feed_service"].create_feed_item.assert_called_once()


@patch("src.domain.services.job_service.feedparser.parse")
def test_process_with_link_contains_filter(mock_parse, job_service, mock_services):
    # GIVEN
    picker = Picker(
        id=1, cronjob="*/5 * * * *", source_id=10, feed_id=20,
        external_id=uuid4(), created_at=datetime(2025, 1, 1, 13, 0, 0)
    )
    mock_services["picker_service"].get_picker_by_id.return_value = picker
    filter_mock = MagicMock(operation=Operation.link_contains, args="['example.com', 1]")
    mock_services["filter_service"].get_filters_by_picker_id.return_value = [filter_mock]
    mock_services["feed_service"].get_feed_items.return_value = []
    mock_services["source_service"].get_source_by_id.return_value = AttrDict(
        url="http://example.com/feed", name="Example Source"
    )

    mock_parse.return_value.entries = [
        AttrDict(
            link="http://example.com/article",
            title="Article 123",
            description="Some text"
        )
    ]

    # WHEN
    job_service.process(picker_id=1)

    # THEN
    mock_services["feed_service"].create_feed_item.assert_called_once()


@patch("src.domain.services.job_service.feedparser.parse")
def test_process_with_description_contains_filter_fails(mock_parse, job_service, mock_services):
    # GIVEN
    picker = Picker(
        id=1, cronjob="*", source_id=10, feed_id=20, external_id=uuid4(), created_at=datetime.now()
    )
    mock_services["picker_service"].get_picker_by_id.return_value = picker
    filter_mock = MagicMock(operation=Operation.description_contains, args="['banana', 2]")
    mock_services["filter_service"].get_filters_by_picker_id.return_value = [filter_mock]
    mock_services["feed_service"].get_feed_items.return_value = []
    mock_services["source_service"].get_source_by_id.return_value = AttrDict(
        url="http://feed", name="Example Source"
    )

    mock_parse.return_value.entries = [
        AttrDict(link="http://item", title="Any", description="banana only once")
    ]

    # WHEN
    job_service.process(picker_id=1)

    # THEN
    mock_services["feed_service"].create_feed_item.assert_not_called()


@patch("src.domain.services.job_service.ast.literal_eval", return_value=["spam", 1])
@patch("src.domain.services.job_service.feedparser.parse")
def test_process_with_title_does_not_contain_filter(mock_parse, job_service, mock_services):
    # GIVEN
    picker = Picker(
        id=1,
        cronjob="*",
        source_id=10,
        feed_id=20,
        external_id=uuid4(),
        created_at=datetime.now()
    )
    mock_services["picker_service"].get_picker_by_id.return_value = picker
    filter_mock = MagicMock(operation=Operation.title_does_not_contain, args="['spam', 1]")
    mock_services["filter_service"].get_filters_by_picker_id.return_value = [filter_mock]
    mock_services["feed_service"].get_feed_items.return_value = []
    mock_services["source_service"].get_source_by_id.return_value = AttrDict(
        url="http://feed", name="Example Source"
    )

    mock_parse.return_value.entries = [
        AttrDict(link="http://item2", title="spam stuff", description="oops")
    ]

    # WHEN
    job_service.process(picker_id=1)

    # THEN
    mock_services["feed_service"].create_feed_item.assert_not_called()


@patch("src.domain.services.job_service.ast.literal_eval", return_value=["spam", 1])
@patch("src.domain.services.job_service.feedparser.parse")
def test_process_with_link_does_not_contain_filter(mock_parse, job_service, mock_services):
    # GIVEN
    picker = Picker(
        id=1,
        cronjob="*",
        source_id=10,
        feed_id=20,
        external_id=uuid4(),
        created_at=datetime.now()
    )
    mock_services["picker_service"].get_picker_by_id.return_value = picker
    filter_mock = MagicMock(operation=Operation.link_does_not_contain, args="['item', 1]")
    mock_services["filter_service"].get_filters_by_picker_id.return_value = [filter_mock]
    mock_services["feed_service"].get_feed_items.return_value = []
    mock_services["source_service"].get_source_by_id.return_value = AttrDict(
        url="http://feed", name="Example Source"
    )

    mock_parse.return_value.entries = [
        AttrDict(link="http://item2", title="spam stuff", description="oops")
    ]

    # WHEN
    job_service.process(picker_id=1)

    # THEN
    mock_services["feed_service"].create_feed_item.assert_not_called()


@patch("src.domain.services.job_service.feedparser.parse")
def test_process_with_description_does_not_contain_filter(mock_parse, job_service, mock_services):
    # GIVEN
    picker = Picker(
        id=1, cronjob="*", source_id=10, feed_id=20, external_id=uuid4(), created_at=datetime.now()
    )
    mock_services["picker_service"].get_picker_by_id.return_value = picker
    filter_mock = MagicMock(operation=Operation.description_does_not_contain, args="['error', 1]")
    mock_services["filter_service"].get_filters_by_picker_id.return_value = [filter_mock]
    mock_services["feed_service"].get_feed_items.return_value = []
    mock_services["source_service"].get_source_by_id.return_value = AttrDict(
        url="http://feed", name="Example Source"
    )

    mock_parse.return_value.entries = [
        AttrDict(link="http://ok", title="Good", description="All fine"),
        AttrDict(link="http://bad", title="Oops", description="error inside"),
    ]

    # WHEN
    job_service.process(picker_id=1)

    # THEN
    assert mock_services["feed_service"].create_feed_item.call_count == 1
    feed_item = mock_services["feed_service"].create_feed_item.call_args[0][0]
    assert feed_item.link == "http://ok"
