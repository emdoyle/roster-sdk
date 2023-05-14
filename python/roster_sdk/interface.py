from abc import ABC, abstractmethod

from roster_sdk.models.chat import ChatMessage


class RosterAgentInterface(ABC):
    @abstractmethod
    async def chat(self, chat_history: list[ChatMessage]) -> str:
        """Respond to a prompt"""

    @abstractmethod
    async def execute_task(self, name: str, description: str) -> None:
        """Execute a task on the agent"""
