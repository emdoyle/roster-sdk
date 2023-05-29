from abc import ABC, abstractmethod

from roster_sdk.config import AgentConfig
from roster_sdk.models.chat import ChatMessage


class RosterAgentInterface(ABC):
    @abstractmethod
    async def chat(self, chat_history: list[ChatMessage]) -> str:
        """Respond to a prompt"""

    @abstractmethod
    async def execute_task(self, name: str, description: str) -> None:
        """Execute a task on the agent"""


class BaseRosterAgent(RosterAgentInterface, ABC):
    def __init__(self):
        self.config = AgentConfig.from_env()

    @property
    def agent_name(self) -> str:
        return self.config.roster_agent_name

    @property
    def agent_port(self) -> int:
        return self.config.roster_agent_port

    @property
    def roster_runtime_ip(self) -> str:
        return self.config.roster_runtime_ip
