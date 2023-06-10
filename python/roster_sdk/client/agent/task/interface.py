from typing import TypeVar, Union

from roster_sdk.client.base import RosterClient
from roster_sdk.models.resources.task import TaskAssignment, TaskStatus

T = TypeVar("T")

# A bit strange, but since this interface is for text I/O based Agents,
# we can use a string to represent an error message.
Result = Union[str, T]


class TaskInterface:
    def __init__(self, agent_name: str, client: RosterClient):
        self.agent_name = agent_name
        self.client = client

    @classmethod
    def from_env(cls, agent_name: str) -> "TaskInterface":
        return cls(agent_name, RosterClient.from_env())

    def finish_task(
        self,
        task: str,
        description: str,
        assignment: TaskAssignment,
        result: str,
        error: str,
    ):
        """Send task result to Roster"""
        updated_task_status = TaskStatus(
            name=task,
            description=description,
            assignment=assignment,
            result=result,
            error=error,
        )
        status_update_event = {
            "event_type": "PUT",
            "resource_type": "TASK",
            "namespace": "default",
            "name": task,
            "status": updated_task_status.dict(),
        }
        self.client.status_update(status_update_event)

    async def execute_subtask(self, task: str, description: str) -> str:
        """Asynchronously execute a subtask and receive its result"""
        return "This isn't implemented yet"
