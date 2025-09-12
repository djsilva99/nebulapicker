from pydantic import BaseModel
from src.domain.models.job import JobRequest


class CreateJobRequest(BaseModel):
    func_name: str
    args: list[str]
    schedule: str


class CreateJobResponse(BaseModel):
    msg: str = "Job created"


def map_create_job_request_to_job_request(
    create_job_request: CreateJobRequest
) -> JobRequest:
    return JobRequest(
        func_name=create_job_request.func_name,
        args=create_job_request.args,
        schedule=create_job_request.schedule
    )
