import asyncio

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from roster_sdk.config import AgentConfig
from roster_sdk.models.api.activity import ActivityEvent, ExecutionType
from roster_sdk.models.api.chat import ChatArgs, ChatResponse
from roster_sdk.models.api.task import ExecuteTaskArgs

from . import errors
from .context import set_agent_activity_context
from .interface import RosterAgentInterface
from .logs import get_logger, get_roster_activity_logger

logger = get_logger()


class Entrypoint:
    def __init__(self, agent: RosterAgentInterface, config: AgentConfig):
        self.agent = agent
        self.config = config
        self.app = FastAPI(title="Roster Agent", version="0.1.0")
        self.setup_routes()
        self.activity_stream = asyncio.Queue()

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
            set_agent_activity_context(
                execution_id="chat",
                execution_type=ExecutionType.CHAT,
                identity=args.identity,
                team=args.team,
                role=args.role,
            )
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
            set_agent_activity_context(
                execution_id=args.task,
                execution_type=ExecutionType.TASK,
                identity=args.assignment.identity_name,
                team=args.assignment.team_name,
                role=args.assignment.role_name,
            )
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
            except errors.RosterAgentTaskException as e:
                raise HTTPException(status_code=404, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/activity-stream")
        async def events(request: Request):
            def listener(event: ActivityEvent):
                self.activity_stream.put_nowait(event.serialize() + b"\n\n")

            async def event_stream():
                try:
                    while True:
                        if await request.is_disconnected():
                            logger.debug(f"Client disconnected ({request.client.host})")
                            break

                        result = await self.activity_stream.get()
                        logger.debug(f"SSE Send ({request.client.host})")
                        yield result
                except asyncio.CancelledError:
                    logger.debug(f"Stopping SSE stream for {request.client.host}")
                    get_roster_activity_logger().remove_listener(listener)

            get_roster_activity_logger().add_listener(listener)

            response = StreamingResponse(event_stream(), media_type="text/event-stream")
            response.headers["Cache-Control"] = "no-cache"
            response.headers["Connection"] = "keep-alive"
            response.headers["Transfer-Encoding"] = "chunked"

            logger.debug(f"Started SSE stream for {request.client.host}")
            return response

    def run(self):
        if not self.config.is_valid:
            raise ValueError(
                "Invalid Roster Agent configuration. Verify environment variables."
            )

        uvicorn.run(self.app, host="0.0.0.0", port=self.config.roster_agent_port)
