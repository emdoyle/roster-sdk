import os
from dataclasses import dataclass
from typing import Optional

from .interface import RosterAgentInterface


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

    @classmethod
    def from_env(cls, agent: RosterAgentInterface):
        config = Config.from_env()
        return cls(agent=agent, config=config)

    def run(self):
        if not self.config.is_valid:
            raise ValueError(
                "Invalid Roster Agent configuration. Verify environment variables."
            )

        # Here is where the FastAPI server should start up
        # implies we need route handlers etc.
