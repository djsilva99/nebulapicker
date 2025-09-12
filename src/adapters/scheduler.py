
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.domain.functions import FUNCTIONS
from src.domain.models.job import Job
from src.domain.ports.scheduler_port import SchedulerPort


class Scheduler(SchedulerPort):
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def start(self):
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()

    def add_job(self, job: Job) -> None:
        func = FUNCTIONS.get(job.func_name)
        if not func:
            print(f"Function {job.func_name} not found")
            return
        self.scheduler.add_job(
            func=func,
            trigger=CronTrigger.from_crontab(job.schedule),
            args=job.args,
            replace_existing=True,
        )

    def load_jobs(self, jobs: list[Job]) -> None:
        for job in jobs:
            self.add_job(job)
