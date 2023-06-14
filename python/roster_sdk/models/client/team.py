from typing import Optional

from pydantic import BaseModel, Field
from roster_sdk.client import errors
from roster_sdk.models.resources.team import TeamResource

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
    def from_resource(
        cls, role_name: str, team_name: str, team_resource: TeamResource
    ) -> "TeamContext":
        agent_role = team_resource.get_role(role_name)
        if not agent_role:
            raise errors.TeamMemberNotFound()
        agent = RoleContext.from_role(
            team_name=team_name, role_name=role_name, role=agent_role
        )
        peers = [
            RoleContext.from_role(
                team_name=team_name,
                role_name=role_name,
                role=team_resource.get_role(peer),
            )
            for peer in team_resource.get_role_peers(role_name)
        ]
        manager_role = team_resource.get_role_manager(role_name)
        manager = (
            RoleContext.from_role(
                team_name=team_name,
                role_name=role_name,
                role=team_resource.get_role(manager_role),
            )
            if manager_role
            else None
        )
        return cls(
            name=team_name,
            role=agent,
            peers=peers,
            manager=manager,
        )
