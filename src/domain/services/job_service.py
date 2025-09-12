from src.domain.models.job import JobRequest
from src.domain.ports.job_port import JobPort
from src.domain.ports.scheduler_port import SchedulerPort


class JobService:
    def __init__(self, scheduler: SchedulerPort, job_port: JobPort):
        self.scheduler = scheduler
        self.job_port = job_port

    def add_cronjob(self, job_request: JobRequest):
        job = self.job_port.create(job_request)
        self.scheduler.add_job(job)

    def load_all(self):
        jobs = self.job_port.get_all()
        self.scheduler.load_jobs(jobs)
