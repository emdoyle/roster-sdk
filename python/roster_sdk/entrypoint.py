import os
from dataclasses import dataclass
from typing import Optional

import uvicorn
from fastapi import FastAPI

from .interface import RosterAgentInterface
from .models.chat import ChatMessage


@dataclass
class Config:
    roster_runtime_ip: Optional[str] = None
    roster_agent_name: Optional[str] = None
    roster_agent_port: Optional[int] = None

    @classmethod
    def from_env(cls):
        port = os.getenv("ROSTER_AGENT_PORT")
        if port is not None:
            port = int(port)
        return cls(
            roster_runtime_ip=os.getenv("ROSTER_RUNTIME_IP"),
            roster_agent_name=os.getenv("ROSTER_AGENT_NAME"),
            roster_agent_port=port,
        )

    @property
    def is_valid(self) -> bool:
        return all(
            [
                self.roster_runtime_ip is not None,
                self.roster_agent_name is not None,
                self.roster_agent_port is not None,
            ]
        )


class Entrypoint:
    def __init__(self, agent: RosterAgentInterface, config: Config):
        self.agent = agent
        self.config = config
        self.app = FastAPI(title="Roster Agent", version="0.1.0")
        self.setup_routes()

    @classmethod
    def from_env(cls, agent: RosterAgentInterface):
        config = Config.from_env()
        return cls(agent=agent, config=config)

    def setup_routes(self):
        @self.app.post("/chat")
        async def chat(chat_history: list[ChatMessage]) -> ChatMessage:
            """Respond to a prompt"""
            response = await self.agent.chat(chat_history)
            return ChatMessage(sender=self.config.roster_agent_name, message=response)

        @self.app.post("/execute_task")
        async def execute_task(name: str, description: str) -> None:
            """Execute a task on the agent"""
            return await self.agent.execute_task(name, description)

    def run(self):
        if not self.config.is_valid:
            raise ValueError(
                "Invalid Roster Agent configuration. Verify environment variables."
            )

        uvicorn.run(self.app, host="0.0.0.0", port=self.config.roster_agent_port)
