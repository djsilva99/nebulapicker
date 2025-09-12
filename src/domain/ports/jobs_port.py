from abc import ABC, abstractmethod

from src.domain.models.job import Job, JobRequest


class JobPort(ABC):

    @abstractmethod
    def create(self, job: JobRequest) -> Job:
        pass

    @abstractmethod
    def get_all(self) -> list[Job]:
        pass
