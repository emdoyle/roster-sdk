from typing import Optional

from pydantic import BaseModel, Field, constr
from roster_sdk.models.base import RosterResource


class Role(BaseModel):
    description: str = Field(description="A description of the role.")

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "description": "A description of the role.",
            }
        }


class Layout(BaseModel):
    roles: dict[str, Role] = Field(
        default_factory=dict, description="The roles in the layout."
    )
    peer_groups: dict[str, list[str]] = Field(
        default_factory=dict, description="The peer groups in the layout."
    )
    management_groups: dict[str, list[str]] = Field(
        default_factory=dict, description="The management groups in the layout."
    )

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "roles": {
                    "role1": Role.Config.schema_extra["example"],
                    "role2": Role.Config.schema_extra["example"],
                },
                "peer_groups": {
                    "group1": ["role1", "role2"],
                    "group2": ["role2", "role3"],
                },
                "management_groups": {
                    "manager1": ["role1", "role2"],
                    "manager2": ["role3"],
                },
            }
        }

    @property
    def non_manager_roles(self) -> set[str]:
        return self.roles.keys() - self.management_groups.keys()


class Member(BaseModel):
    identity: str = Field(description="The identity of the member.")
    agent: str = Field(description="The agent running this member.")

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "identity": "Alice",
                "agent": "agent1",
            }
        }


class TeamSpec(BaseModel):
    name: str = Field(description="A name to identify the team.")
    layout: Layout = Field(description="The layout of the team.")
    members: dict[str, Member] = Field(
        default_factory=dict, description="The members of the team."
    )

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "name": "Red Team",
                "layout": Layout.Config.schema_extra["example"],
                "members": {
                    "member1": Member.Config.schema_extra["example"],
                    "member2": Member.Config.schema_extra["example"],
                },
            }
        }

    def get_role(self, role_name: str) -> Optional[Role]:
        return self.layout.roles.get(role_name)

    def get_role_peers(self, role_name: str) -> list[str]:
        peers = []
        # Concatenate all roles in the peer groups that contain the role
        for peer_group in self.layout.peer_groups.values():
            if role_name in peer_group:
                peers.extend(peer_group)
        return peers

    def get_role_manager(self, role_name: str) -> Optional[str]:
        # Find the first manager role that contains the agent's role
        for manager, managed_roles in self.layout.management_groups.items():
            if role_name in managed_roles:
                return manager
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

    def get_role(self, name: str) -> Optional[Role]:
        return self.spec.get_role(name)

    def get_role_manager(self, name: str) -> Optional[str]:
        return self.spec.get_role_manager(name)

    def get_member_by_role(self, role: str) -> Optional[Member]:
        return self.spec.members.get(role)

    def get_role_peers(self, role: str) -> list[str]:
        return self.spec.get_role_peers(role)

    def roles_share_peer_group(self, role_one: str, role_two: str) -> bool:
        for peer in self.spec.get_role_peers(role_one):
            if peer == role_two:
                return True
        return False
