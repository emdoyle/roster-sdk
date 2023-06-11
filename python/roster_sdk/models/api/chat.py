from pydantic import BaseModel, Field

from ..chat import ChatMessage


class ChatArgs(BaseModel):
    messages: list[ChatMessage] = Field(description="The history of the conversation.")
    team: str = Field(
        description="The name of the team, which the agent will use as context for the conversation.",
        default="",
    )

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "messages": [ChatMessage.Config.schema_extra["example"]],
                "team": "my_team",
            }
        }
