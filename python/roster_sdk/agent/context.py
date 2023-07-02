from contextvars import ContextVar
from typing import Optional

from roster_sdk.models.api.activity import AgentContext, ExecutionContext, ExecutionType

agent_execution_context: ContextVar[Optional[ExecutionContext]] = ContextVar(
    "agent_execution_context", default=None
)
agent_context: ContextVar[Optional[AgentContext]] = ContextVar(
    "agent_context", default=None
)


def get_agent_activity_context() -> Optional[tuple[AgentContext, ExecutionContext]]:
    agent_ctx = agent_context.get()
    execution_ctx = agent_execution_context.get()
    if agent_ctx is None or execution_ctx is None:
        return None
    return agent_ctx, execution_ctx


def set_agent_activity_context(
    execution_id: str,
    execution_type: ExecutionType,
    identity: str = "",
    team: str = "",
    role: str = "",
):
    agent_execution_context.set(
        ExecutionContext(
            execution_id=execution_id,
            execution_type=execution_type,
        )
    )
    agent_context.set(
        AgentContext(
            identity=identity,
            team=team,
            role=role,
        )
    )
