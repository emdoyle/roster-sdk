from pydantic import BaseModel, Field

from ..chat import ChatMessage


class ChatArgs(BaseModel):
    identity: str = Field(description="The name of the agent.")
    team: str = Field(description="The name of the team which the agent is on.")
    role: str = Field(description="The role which identifies the agent on the team.")
    messages: list[ChatMessage] = Field(description="The history of the conversation.")

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "identity": "my_identity",
                "team": "my_team",
                "role": "my_role",
                "messages": [ChatMessage.Config.schema_extra["example"]],
            }
        }


class ChatResponse(BaseModel):
    message: str = Field(description="The text of the agent's response.")

    class Config:
        validate_assignment = True
        schema_extra = {"example": {"message": "Hello, world!"}}
