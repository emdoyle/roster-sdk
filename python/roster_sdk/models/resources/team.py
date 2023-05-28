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
        default_factory=list, description="The members of the team."
    )

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "name": "Red Team",
                "layout": TeamLayoutSpec.Config.schema_extra["example"],
                "members": {
                    "agent1": AgentSpec.Config.schema_extra["example"],
                    "agent2": AgentSpec.Config.schema_extra["example"],
                },
            }
        }

    def get_agent_role(self, name: str) -> Optional[RoleSpec]:
        role_name = next(
            (role for role, agent in self.members.items() if agent.name == name), None
        )
        if role_name is None:
            return None
        return self.layout.roles[role_name]


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
