from abc import ABC, abstractmethod


class SchedulerPort(ABC):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass
