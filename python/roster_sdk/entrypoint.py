import os
from dataclasses import dataclass
from typing import Optional

from .interface import RosterAgentInterface


@dataclass
class Config:
    roster_runtime_ip: Optional[str] = None
    roster_agent_name: Optional[str] = None
    task_id: Optional[str] = None
    task_name: Optional[str] = None
    task_description: Optional[str] = None
    conversation_id: Optional[str] = None
    conversation_name: Optional[str] = None
    conversation_port: Optional[str] = None

    @classmethod
    def from_env(cls):
        return cls(
            roster_runtime_ip=os.getenv("ROSTER_RUNTIME_IP"),
            roster_agent_name=os.getenv("ROSTER_AGENT_NAME"),
            task_id=os.getenv("ROSTER_AGENT_TASK_ID"),
            task_name=os.getenv("ROSTER_AGENT_TASK_NAME"),
            task_description=os.getenv("ROSTER_AGENT_TASK_DESCRIPTION"),
            conversation_id=os.getenv("ROSTER_AGENT_CONVERSATION_ID"),
            conversation_name=os.getenv("ROSTER_AGENT_CONVERSATION_NAME"),
            conversation_port=os.getenv("ROSTER_AGENT_CONVERSATION_PORT"),
        )

    @property
    def is_valid_conversation(self) -> bool:
        return all(
            [
                self.roster_agent_name,
                self.conversation_name,
            ]
        )

    @property
    def is_valid_task(self) -> bool:
        return all(
            [
                self.roster_agent_name,
                self.task_name,
                self.task_description,
            ]
        )


class Entrypoint:
    def __init__(self, agent: RosterAgentInterface, config: Config):
        self.agent = agent
        self.config = config

    @classmethod
    def from_env(cls, agent: RosterAgentInterface):
        config = Config.from_env()
        return cls(agent=agent, config=config)

    def run(self):
        if self.config.is_valid_conversation:
            self.agent.start_conversation(
                name=self.config.conversation_name, port=self.config.conversation_port
            )
        elif self.config.is_valid_task:
            self.agent.execute_task(
                name=self.config.task_name,
                description=self.config.task_description,
            )
        else:
            raise ValueError(
                "Invalid Roster Agent configuration. Verify environment variables."
            )
