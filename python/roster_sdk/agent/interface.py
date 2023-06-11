from abc import ABC, abstractmethod

from roster_sdk.client.agent.task.manager import TaskManager
from roster_sdk.config import AgentConfig
from roster_sdk.models.chat import ChatMessage
from roster_sdk.models.resources.task import TaskAssignment


class RosterAgentInterface(ABC):
    @abstractmethod
    async def chat(self, chat_history: list[ChatMessage], team_name: str = "") -> str:
        """Respond to a prompt"""

    @abstractmethod
    async def ack_task(
        self, name: str, description: str, assignment: TaskAssignment
    ) -> bool:
        """Acknowledge and begin executing a task on the agent"""


class BaseRosterAgent(RosterAgentInterface, ABC):
    def __init__(self):
        self.config = AgentConfig.from_env()
        self.task_manager = TaskManager.from_env(self.config.roster_agent_name)

    async def ack_task(
        self, name: str, description: str, assignment: TaskAssignment
    ) -> bool:
        self.task_manager.run_task(self.execute_task, name, description, assignment)
        return True

    @abstractmethod
    async def execute_task(
        self, name: str, description: str, assignment: TaskAssignment
    ) -> str:
        """Execute a task on the agent"""

    @property
    def agent_name(self) -> str:
        return self.config.roster_agent_name

    @property
    def agent_port(self) -> int:
        return self.config.roster_agent_port

    @property
    def roster_runtime_ip(self) -> str:
        return self.config.roster_runtime_ip
