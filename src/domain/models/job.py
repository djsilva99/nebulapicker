from datetime import datetime

from pydantic import BaseModel


class JobRequest(BaseModel):
    func_name: str
    args: list[str]
    schedule: str


class Job(BaseModel):
    id: int
    func_name: str
    args: list[str]
    schedule: str
    created_at: datetime
