import asyncio
import logging
from typing import Callable, Coroutine

from roster_sdk.client import errors
from roster_sdk.models.resources.task import TaskAssignment

from .interface import TaskInterface

TaskExecutor = Callable[..., Coroutine[None, None, str]]

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TaskManager:
    def __init__(self, task_interface: TaskInterface):
        self.task_interface = task_interface
        self.running_tasks: dict[str, asyncio.Task] = {}

    @classmethod
    def from_env(cls, agent_name: str) -> "TaskManager":
        return cls(TaskInterface.from_env(agent_name))

    async def _finish_task(
        self,
        task: str,
        description: str,
        assignment: TaskAssignment,
        result: str,
        error: str,
    ):
        try:
            await self.task_interface.finish_task(
                task, description, assignment, result=result, error=error
            )
        except errors.RosterClientException as e:
            logger.error("Failed to finalize task: %s", task)
            logger.debug("(task-manager) Failed to finalize task %s: %s", task, e)

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
            logger.info("Cancelled task %s", name)
        except Exception as e:
            logger.debug("(task-manager) Task %s failed: %s", name, e)
            await self._finish_task(
                name, description, assignment, result="", error=str(e)
            )
        else:
            await self._finish_task(
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
            raise errors.TaskManagerException(f"Task {name} is already running")
        self.running_tasks[name] = asyncio.create_task(
            self._run_task(task_executor, name, description, assignment)
        )

    def cancel_task(self, task: str) -> None:
        if task not in self.running_tasks:
            raise errors.TaskManagerException(f"Task {task} is not running")
        self.running_tasks[task].cancel()

    def teardown(self):
        for task in self.running_tasks.values():
            task.cancel()
        self.running_tasks = {}
