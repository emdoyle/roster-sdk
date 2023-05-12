from abc import ABC, abstractmethod


class RosterAgentInterface(ABC):
    @abstractmethod
    def start_conversation(self, name: str) -> None:
        """Start a websocket server representing a conversation with the agent"""

    # This is probably not necessary since we just kill the process
    @abstractmethod
    def end_conversation(self) -> None:
        """End the conversation with the agent"""

    @abstractmethod
    def execute_task(self, name: str, description: str) -> None:
        """Execute a task on the agent"""
