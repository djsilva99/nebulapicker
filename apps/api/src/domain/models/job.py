from pydantic import BaseModel


class Job(BaseModel):
    func_name: str
    args: list
    schedule: str
