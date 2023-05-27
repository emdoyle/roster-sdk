from pydantic import BaseModel, Field, constr
from roster_sdk import constants


class RosterResource(BaseModel):
    api_version: constr(regex="^v[0-9.]+$") = Field(
        default=constants.API_VERSION, description="The api version."
    )
    kind: str = Field(description="The kind of resource.")
    metadata: dict[str, str] = Field(
        default_factory=dict, description="The metadata of the agent."
    )

    class Config:
        validate_assignment = True
