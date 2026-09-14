from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from src.adapters.scheduler import Scheduler


@pytest.fixture
def scheduler():
    """
    Create a Scheduler without creating a real repository/session.
    """
    with patch("src.adapters.scheduler.PickersRepository") as mock_repository:
        scheduler = Scheduler()
        scheduler.pickers_repository = mock_repository.return_value
        yield scheduler


@pytest.fixture
def picker():
    picker = MagicMock()
    picker.id = 123
    picker.cronjob = "*/5 * * * *"
    return picker


def test_scheduler_initial_state(scheduler):
    assert scheduler._running is False
    assert scheduler._thread is None


def test_start_starts_scheduler_thread(scheduler):
    with patch("src.adapters.scheduler.threading.Thread") as mock_thread:
        mock_thread_instance = mock_thread.return_value

        scheduler.start()

        assert scheduler._running is True

        mock_thread.assert_called_once_with(
            target=scheduler._run,
            daemon=True,
        )

        mock_thread_instance.start.assert_called_once()

        assert scheduler._thread == mock_thread_instance


def test_start_does_nothing_if_already_running(scheduler):
    scheduler._running = True

    with patch("src.adapters.scheduler.threading.Thread") as mock_thread:
        scheduler.start()

        mock_thread.assert_not_called()


def test_shutdown_stops_scheduler(scheduler):
    mock_thread = MagicMock()

    scheduler._running = True
    scheduler._thread = mock_thread

    scheduler.shutdown()

    assert scheduler._running is False

    mock_thread.join.assert_called_once_with(timeout=5)


def test_shutdown_without_thread(scheduler):
    scheduler._running = True
    scheduler._thread = None

    scheduler.shutdown()

    assert scheduler._running is False


def test_schedule_due_pickers(scheduler, picker):
    next_fetch = datetime(2026, 9, 13, 10, 5)

    scheduler.pickers_repository.get_due_pickers.return_value = [picker]

    with (
        patch("src.adapters.scheduler.process_picker") as mock_process_picker,
        patch("src.adapters.scheduler.croniter") as mock_croniter,
        patch("src.adapters.scheduler.datetime") as mock_datetime,
    ):
        now = datetime(2026, 9, 13, 10, 0)

        mock_datetime.now.return_value = now

        mock_cron = mock_croniter.return_value
        mock_cron.get_next.return_value = next_fetch

        scheduler._schedule_due_pickers()

    scheduler.pickers_repository.get_due_pickers.assert_called_once_with(now)

    mock_process_picker.delay.assert_called_once_with(picker.id)

    mock_croniter.assert_called_once_with(
        picker.cronjob,
        now,
    )

    scheduler.pickers_repository.update_next_fetch.assert_called_once_with(
        picker.id,
        next_fetch,
    )


def test_schedule_due_pickers_with_no_pickers(scheduler):
    scheduler.pickers_repository.get_due_pickers.return_value = []

    with patch("src.adapters.scheduler.process_picker") as mock_process_picker:
        scheduler._schedule_due_pickers()

    mock_process_picker.delay.assert_not_called()

    scheduler.pickers_repository.update_next_fetch.assert_not_called()


def test_schedule_multiple_due_pickers(scheduler):
    picker1 = MagicMock()
    picker1.id = 1
    picker1.cronjob = "*/5 * * * *"

    picker2 = MagicMock()
    picker2.id = 2
    picker2.cronjob = "0 * * * *"

    next_fetch_1 = datetime(2026, 9, 13, 10, 5)
    next_fetch_2 = datetime(2026, 9, 13, 11, 0)

    scheduler.pickers_repository.get_due_pickers.return_value = [
        picker1,
        picker2,
    ]

    with (
        patch("src.adapters.scheduler.process_picker") as mock_process_picker,
        patch("src.adapters.scheduler.croniter") as mock_croniter,
        patch("src.adapters.scheduler.datetime") as mock_datetime,
    ):
        now = datetime(2026, 9, 13, 10, 0)
        mock_datetime.now.return_value = now

        mock_croniter.side_effect = [
            MagicMock(),
            MagicMock(),
        ]

        mock_croniter.return_value.get_next.return_value = next_fetch_1

        # Configure individual croniter instances.
        croniter_1 = MagicMock()
        croniter_1.get_next.return_value = next_fetch_1

        croniter_2 = MagicMock()
        croniter_2.get_next.return_value = next_fetch_2

        mock_croniter.side_effect = [
            croniter_1,
            croniter_2,
        ]

        scheduler._schedule_due_pickers()

    assert mock_process_picker.delay.call_count == 2

    mock_process_picker.delay.assert_any_call(1)
    mock_process_picker.delay.assert_any_call(2)

    assert (
        scheduler.pickers_repository.update_next_fetch.call_count
        == 2
    )

    scheduler.pickers_repository.update_next_fetch.assert_any_call(
        1,
        next_fetch_1,
    )

    scheduler.pickers_repository.update_next_fetch.assert_any_call(
        2,
        next_fetch_2,
    )


def test_run_calls_schedule_and_sleeps(scheduler):
    scheduler._running = True

    with (
        patch.object(
            scheduler,
            "_schedule_due_pickers",
            side_effect=[
                None,
                KeyboardInterrupt,
            ],
        ) as mock_schedule,
        patch("src.adapters.scheduler.time.sleep") as mock_sleep,
    ):
        # KeyboardInterrupt is not caught by `except Exception`,
        # so it allows us to stop the infinite loop in the test.
        with pytest.raises(KeyboardInterrupt):
            scheduler._run()

    assert mock_schedule.call_count == 2
    mock_sleep.assert_called_once()


def test_run_continues_when_scheduling_fails(scheduler):
    scheduler._running = True

    with (
        patch.object(
            scheduler,
            "_schedule_due_pickers",
            side_effect=Exception("database error"),
        ) as mock_schedule,
        patch(
            "src.adapters.scheduler.time.sleep",
            side_effect=lambda _: setattr(
                scheduler,
                "_running",
                False,
            ),
        ),
    ):
        scheduler._run()

    mock_schedule.assert_called_once()
