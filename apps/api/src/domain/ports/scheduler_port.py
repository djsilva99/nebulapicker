from abc import ABC, abstractmethod

from src.domain.models.job import Job


class SchedulerPort(ABC):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass

    @abstractmethod
    def add_job(self, job: Job) -> None:
        pass

    @abstractmethod
    def load_jobs(self, jobs: list[Job]) -> None:
        pass

    @abstractmethod
    def delete_job(self, job: Job) -> None:
        pass
