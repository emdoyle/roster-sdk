from pydantic import BaseModel, Field
from roster_sdk.models.resources.role import RoleSpec

# Context is from the perspective of a specific Agent,
# in contrast to Resource which is from the perspective of the Roster API.
# In this case, Agent is part of a team, and each RoleContext is a role
# on the team. (not necessarily the Agent's role)


class RoleContext(BaseModel):
    team: str = Field(description="The name of the team.")
    role: str = Field(description="The name of the role.")
    description: str = Field(description="A description of the role.")

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "team": "Red",
                "role": "Role Manager",
                "description": "A description of the role.",
            }
        }

    @classmethod
    def from_spec(cls, team: str, spec: RoleSpec) -> "RoleContext":
        return cls(
            team=team,
            role=spec.name,
            description=spec.description,
        )
