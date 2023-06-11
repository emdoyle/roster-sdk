import uvicorn
from fastapi import FastAPI
from roster_sdk.config import AgentConfig
from roster_sdk.models.api.chat import ChatArgs
from roster_sdk.models.api.task import ExecuteTaskArgs
from roster_sdk.models.chat import ChatMessage

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
        async def chat(args: ChatArgs) -> ChatMessage:
            """Respond to a prompt"""
            response = await self.agent.chat(args.messages, team_name=args.team)
            return ChatMessage(sender=self.config.roster_agent_name, message=response)

        @self.app.post("/tasks")
        async def execute_task(args: ExecuteTaskArgs) -> bool:
            """Execute a task on the agent"""
            return await self.agent.ack_task(
                args.task, args.description, args.assignment
            )

    def run(self):
        if not self.config.is_valid:
            raise ValueError(
                "Invalid Roster Agent configuration. Verify environment variables."
            )

        uvicorn.run(self.app, host="0.0.0.0", port=self.config.roster_agent_port)
