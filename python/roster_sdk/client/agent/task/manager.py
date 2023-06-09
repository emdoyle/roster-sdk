import asyncio
from typing import Callable, Coroutine

from roster_sdk.models.resources.task import TaskAssignment

from .interface import TaskInterface

TaskExecutor = Callable[..., Coroutine[None, None, str]]


class TaskManager:
    def __init__(self, task_interface: TaskInterface):
        self.task_interface = task_interface
        self.running_tasks: dict[str, asyncio.Task] = {}

    @classmethod
    def from_env(cls, agent_name: str) -> "TaskManager":
        return cls(TaskInterface.from_env(agent_name))

    async def _run_task(
        self,
        task_executor: TaskExecutor,
        name: str,
        description: str,
        assignment: TaskAssignment,
    ):
        try:
            result = await task_executor(name, description, assignment)
        except asyncio.CancelledError:
            self.task_interface.finish_task(
                name, description, assignment, result="", error="Task cancelled"
            )
        except Exception as e:
            self.task_interface.finish_task(
                name, description, assignment, result="", error=str(e)
            )
        else:
            self.task_interface.finish_task(
                name, description, assignment, result=result, error=""
            )
        finally:
            del self.running_tasks[name]

    def run_task(
        self,
        task_executor: TaskExecutor,
        name: str,
        description: str,
        assignment: TaskAssignment,
    ) -> None:
        if name in self.running_tasks:
            raise ValueError(f"Task {name} is already running")
        self.running_tasks[name] = asyncio.create_task(
            self._run_task(task_executor, name, description, assignment)
        )

    def teardown(self):
        for task in self.running_tasks.values():
            task.cancel()
        self.running_tasks = {}
