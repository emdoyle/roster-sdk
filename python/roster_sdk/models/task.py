from pydantic import BaseModel, Field


class Task(BaseModel):
    name: str = Field(description="The name of the task.")
    description: str = Field(description="The description of the task.")

    class Config:
        validate_assignment = True
        schema_extra = {
            "example": {
                "name": "my_task",
                "description": "my task",
            }
        }
