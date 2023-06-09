from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    name: str = Field(description="The name of the agent.")
    teams: list[str] = Field(
        default_factory=list, description="The teams that the agent is a member of."
    )

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "name": "agent1",
                "teams": ["team1", "team2"],
            }
        }
