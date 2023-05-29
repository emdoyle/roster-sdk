import os
from dataclasses import dataclass
from typing import Optional

from environs import Env

env = Env()
env.read_env()

# Roster API Config
ROSTER_API_URL = env.str("ROSTER_API_URL", "http://localhost:7888/v0.1")
ROSTER_API_EVENTS_PATH = env.str("ROSTER_API_EVENTS_PATH", "/resource-events")
ROSTER_API_AGENTS_PATH = env.str("ROSTER_API_AGENTS_PATH", "/agents")
ROSTER_API_TASKS_PATH = env.str("ROSTER_API_TASKS_PATH", "/task")
ROSTER_API_CONVERSATIONS_PATH = env.str(
    "ROSTER_API_CONVERSATIONS_PATH", "/conversation"
)
ROSTER_API_ROLES_PATH = env.str("ROSTER_API_ROLES_PATH", "/roles")
ROSTER_API_TEAMS_PATH = env.str("ROSTER_API_TEAMS_PATH", "/teams")
ROSTER_API_TEAM_LAYOUTS_PATH = env.str("ROSTER_API_TEAM_LAYOUTS_PATH", "/team-layouts")
ROSTER_API_COMMANDS_PATH = env.str("ROSTER_API_COMMANDS_PATH", "/commands")


@dataclass
class AgentConfig:
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