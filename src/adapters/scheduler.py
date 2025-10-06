from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.base import JobLookupError
from src.domain.handlers import HANDLERS
from src.domain.models.job import Job
from src.domain.ports.scheduler_port import SchedulerPort


class Scheduler(SchedulerPort):
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def start(self):
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()

    def _build_job_id(self, job: Job) -> str:
        args_str = "_".join(map(str, job.args)) if job.args else "noargs"
        return f"{job.func_name}_{args_str}".replace(" ", "_")

    def add_job(self, job: Job) -> None:
        func = HANDLERS.get(job.func_name)
        if not func:
            print(f"Function {job.func_name} not found")
            return

        job_id = self._build_job_id(job)

        self.scheduler.add_job(
            func=func,
            trigger=CronTrigger.from_crontab(job.schedule),
            args=job.args,
            id=job_id,
            replace_existing=True,
        )

    def load_jobs(self, jobs: list[Job]) -> None:
        for job in jobs:
            self.add_job(job)

    def delete_job(self, job: Job) -> None:
        job_id = self._build_job_id(job)
        try:
            self.scheduler.remove_job(job_id)
            print(f"Removed job: {job_id}")
        except JobLookupError:
            print(f"Job {job_id} not found in scheduler.")
