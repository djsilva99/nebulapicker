import threading
import time
from datetime import datetime

from croniter import croniter
from src.adapters.repositories.pickers_repository import PickersRepository
from src.configs.database import SessionLocal
from src.configs.settings import Settings
from src.tasks import process_picker

settings: Settings = Settings()


class Scheduler:

    def __init__(self):
        self.pickers_repository = PickersRepository(SessionLocal)

        self._running = False
        self._thread: threading.Thread | None = None

    def start(self):
        if self._running:
            return

        self._running = True

        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
        )

        self._thread.start()

    def shutdown(self):
        self._running = False

        if self._thread:
            self._thread.join(timeout=5)

    def _run(self):
        while self._running:
            try:
                self._schedule_due_pickers()
            except Exception:
                pass

            time.sleep(settings.SCHEDULER_INTERVAL_SECONDS)
            #time.sleep(self.CHECK_INTERVAL_SECONDS)

    def _schedule_due_pickers(self):
        now = datetime.now()

        pickers = self.pickers_repository.get_due_pickers(now)
        for picker in pickers:
            process_picker.delay(picker.id)

            next_fetch = croniter(picker.cronjob, datetime.now()).get_next(datetime)

            # Prevent the picker from being scheduled again
            # until its next_fetch time.
            self.pickers_repository.update_next_fetch(
                picker.id,
                next_fetch,
            )


if __name__ == "__main__":
    scheduler = Scheduler()

    try:
        scheduler.start()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        scheduler.shutdown()
