import uvicorn
from fastapi import FastAPI
from roster_sdk.models.chat import ChatMessage
from roster_sdk.models.resources.task import TaskAssignment, TaskSpec

from ..config import AgentConfig
from .interface import RosterAgentInterface


class Entrypoint:
    def __init__(self, agent: RosterAgentInterface, config: AgentConfig):
        self.agent = agent
        self.config = config
        self.app = FastAPI(title="Roster Agent", version="0.1.0")
        self.setup_routes()

    @classmethod
    def from_env(cls, agent: RosterAgentInterface):
        config = AgentConfig.from_env()
        return cls(agent=agent, config=config)

    def setup_routes(self):
        @self.app.get("/healthcheck")
        async def healthcheck() -> bool:
            """Healthcheck"""
            return True

        @self.app.post("/chat")
        async def chat(chat_history: list[ChatMessage]) -> ChatMessage:
            """Respond to a prompt"""
            response = await self.agent.chat(chat_history)
            return ChatMessage(sender=self.config.roster_agent_name, message=response)

        @self.app.post("/task")
        async def execute_task(
            name: str, description: str, assignment: TaskAssignment
        ) -> bool:
            """Execute a task on the agent"""
            return await self.agent.ack_task(name, description, assignment)

    def run(self):
        if not self.config.is_valid:
            raise ValueError(
                "Invalid Roster Agent configuration. Verify environment variables."
            )

        uvicorn.run(self.app, host="0.0.0.0", port=self.config.roster_agent_port)
