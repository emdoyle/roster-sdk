from typing import Optional

from pydantic import BaseModel, Field, constr
from roster_sdk.models.base import RosterResource

from .agent import AgentSpec
from .role import RoleSpec
from .team_layout import TeamLayoutSpec


class TeamSpec(BaseModel):
    name: str = Field(description="A name to identify the team.")
    layout: TeamLayoutSpec = Field(description="The layout of the team.")
    members: dict[str, AgentSpec] = Field(
        default_factory=dict, description="The members of the team."
    )

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "name": "Red Team",
                "layout": TeamLayoutSpec.Config.schema_extra["example"],
                "members": {
                    "role1": AgentSpec.Config.schema_extra["example"],
                    "role2": AgentSpec.Config.schema_extra["example"],
                },
            }
        }

    def get_agent_role(self, name: str) -> Optional[RoleSpec]:
        role_name = next(
            (role for role, agent in self.members.items() if agent.name == name),
            None,
        )
        if role_name is None:
            return None
        return self.layout.roles[role_name]

    def get_role_peers(self, role: str) -> list[RoleSpec]:
        peers = []
        # Concatenate all roles in the peer groups that contain the role
        for peer_group in self.layout.peer_groups.values():
            if role in peer_group:
                peers += [self.layout.roles[peer] for peer in peer_group]
        return peers

    def get_agent_peers(self, name: str) -> list[RoleSpec]:
        role = self.get_agent_role(name)
        if role is None:
            return []
        return self.get_role_peers(role.name)

    def get_agent_manager(self, name: str) -> Optional[RoleSpec]:
        role = self.get_agent_role(name)
        if role is None:
            return None
        # Find the first manager role that contains the agent's role
        for manager, managed_roles in self.layout.management_groups.items():
            if role.name in managed_roles:
                return self.layout.roles[manager]
        return None


class TeamStatus(BaseModel):
    name: str = Field(description="A name to identify the team.")
    status: str = Field(default="active", description="The status of the team.")

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "name": "Red Team",
                "status": "active",
            }
        }


class TeamResource(RosterResource):
    kind: constr(regex="^Team$") = Field(
        default="Team", description="The kind of resource."
    )
    spec: TeamSpec = Field(description="The specification of the team.")
    status: TeamStatus = Field(description="The status of the team.")

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "spec": TeamSpec.Config.schema_extra["example"],
                "status": TeamStatus.Config.schema_extra["example"],
            }
        }

    @classmethod
    def initial_state(cls, spec: TeamSpec) -> "TeamResource":
        return cls(spec=spec, status=TeamStatus(name=spec.name))

    def get_agent_role(self, name: str) -> Optional[RoleSpec]:
        return self.spec.get_agent_role(name)

    def get_agent_manager(self, name: str) -> Optional[RoleSpec]:
        return self.spec.get_agent_manager(name)

    def get_member_by_role(self, role: str) -> Optional[AgentSpec]:
        return self.spec.members.get(role)

    def roles_share_peer_group(self, role_one: str, role_two: str) -> bool:
        for peer in self.spec.get_role_peers(role_one):
            if peer.name == role_two:
                return True
        return False
