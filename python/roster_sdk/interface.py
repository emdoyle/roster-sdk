from abc import ABC, abstractmethod
from typing import Optional


class RosterAgentInterface(ABC):
    @abstractmethod
    def start_conversation(self, name: str, port: Optional[int] = None) -> None:
        """Start a websocket server representing a conversation with the agent"""

    @abstractmethod
    def end_conversation(self) -> None:
        """End the conversation with the agent"""

    @abstractmethod
    def execute_task(self, name: str, description: str) -> None:
        """Execute a task on the agent"""
