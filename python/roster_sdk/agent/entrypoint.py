import uvicorn
from fastapi import FastAPI, HTTPException
from roster_sdk.config import AgentConfig
from roster_sdk.models.api.chat import ChatArgs, ChatResponse
from roster_sdk.models.api.task import ExecuteTaskArgs

from . import errors
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
        async def chat(args: ChatArgs) -> ChatResponse:
            """Respond to a prompt"""
            response = await self.agent.chat(
                identity=args.identity,
                team=args.team,
                role=args.role,
                chat_history=args.messages,
            )
            return ChatResponse(message=response)

        @self.app.post("/tasks")
        async def execute_task(args: ExecuteTaskArgs) -> bool:
            """Execute a task on the agent"""
            try:
                await self.agent.ack_task(args.task, args.description, args.assignment)
                return True
            except errors.RosterAgentTaskAlreadyExists as e:
                raise HTTPException(status_code=409, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/tasks/{task}")
        async def cancel_task(task: str) -> bool:
            """Cancel a task"""
            try:
                await self.agent.cancel_task(task)
                return True
            except errors.RosterAgentTaskNotFound as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    def run(self):
        if not self.config.is_valid:
            raise ValueError(
                "Invalid Roster Agent configuration. Verify environment variables."
            )

        uvicorn.run(self.app, host="0.0.0.0", port=self.config.roster_agent_port)
