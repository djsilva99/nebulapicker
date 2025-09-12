from sqlalchemy import text
from sqlalchemy.orm import Session
from src.domain.models.job import Job, JobRequest
from src.domain.ports.job_port import JobPort
import json


class JobRepository(JobPort):

    def __init__(self, db: Session):
        self.db = db

    def create(self, job: JobRequest) -> Job:
        sql = text(
            "INSERT INTO jobs (func_name, args, schedule) VALUES (:func_name, :args, :schedule) RETURNING id, func_name, args, schedule, created_at"
        )
        result = self.db.execute(
            sql,
            {
                "func_name": job.func_name,
                "args": json.dumps(job.args),
                "schedule": job.schedule
            }
        ).first()

        self.db.commit()

        data = result._mapping
        return Job(
            id=data["id"],
            func_name=data["func_name"],
            args=json.loads(data["args"]),
            schedule=data["schedule"],
            created_at=data["created_at"],
        )

    def get_all(self) -> list[Job]:
        sql = text("SELECT id, func_name, args, schedule, created_at FROM jobs")
        result = self.db.execute(sql)

        if result:
            jobs: list[Job] = []
            for row in result:
                data = row._mapping
                jobs.append(
                    Job(
                        id=data["id"],
                        func_name=data["func_name"],
                        args=json.loads(data["args"]),
                        schedule=data["schedule"],
                        created_at=data["created_at"],
                    )
                )
            return jobs
        return []
