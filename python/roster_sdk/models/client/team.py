from typing import Optional

from pydantic import BaseModel, Field

from ..resources.team import TeamSpec
from .role import RoleContext

# Context is from the perspective of a specific Agent,
# in contrast to Resource which is from the perspective of the Roster API.
# In this case, the Team Context is trimmed to only the role, peers, and managers
# of the Agent.


class TeamContext(BaseModel):
    name: str = Field(description="The name of the team.")
    role: RoleContext = Field(description="The Agent's role in the team layout.")
    peers: list[RoleContext] = Field(
        default_factory=list, description="The Agent's peers in the team layout."
    )
    manager: Optional[RoleContext] = Field(
        description="The Agent's manager in the team layout."
    )

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "name": "Red Team",
                "role": RoleContext.Config.schema_extra["example"],
                "peer_groups": {
                    "group1": ["role1", "role2"],
                    "group2": ["role2", "role3"],
                },
                "manager": "manager1",
            }
        }

    @classmethod
    def from_spec(cls, agent: str, spec: TeamSpec) -> "TeamContext":
        team = spec.name
        agent_role = spec.get_agent_role(agent)
        if agent_role is None:
            raise ValueError(f"Agent {agent} is not a member of team {team}.")
        peers = spec.get_agent_peers(agent)
        manager = spec.get_agent_manager(agent)
        return cls(
            name=team,
            role=RoleContext.from_spec(team, agent_role),
            peers=[RoleContext.from_spec(team, peer) for peer in peers],
            manager=RoleContext.from_spec(team, manager)
            if manager is not None
            else None,
        )
