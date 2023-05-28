from pydantic import BaseModel, Field

from .role import RoleContext


class TeamLayoutContext(BaseModel):
    roles: dict[str, RoleContext] = Field(
        default_factory=list, description="The roles of the team layout."
    )
    peer_groups: dict[str, list[str]] = Field(
        default_factory=list, description="The peer groups of the team layout."
    )
    management_groups: dict[str, list[str]] = Field(
        default_factory=list, description="The management groups of the team layout."
    )

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "roles": {
                    "role1": RoleContext.Config.schema_extra["example"],
                    "role2": RoleContext.Config.schema_extra["example"],
                },
                "peer_groups": {
                    "group1": ["role1", "role2"],
                    "group2": ["role2", "role3"],
                },
                "management_groups": {
                    "manager1": ["role1", "role2"],
                    "manager2": ["role2", "role2"],
                },
            }
        }


class TeamContext(BaseModel):
    name: str = Field(description="The name of the team.")
    layout: TeamLayoutContext = Field(description="The layout of the team.")

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "name": "Red Team",
                "layout": TeamLayoutContext.Config.schema_extra["example"],
            }
        }
