from abc import ABC, abstractmethod


class RosterAgentTaskInterface(ABC):
    @abstractmethod
    async def get_task_context(self, task: str) -> dict:
        pass

    @abstractmethod
    async def get_current_tasks(self) -> list[str]:
        pass

    @abstractmethod
    async def request_task_execution(self, task: str) -> str:
        pass
