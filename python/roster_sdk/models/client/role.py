from pydantic import BaseModel, Field


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
