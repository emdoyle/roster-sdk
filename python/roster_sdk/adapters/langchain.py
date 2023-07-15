from roster_sdk.agent.logs import get_logger, get_roster_activity_logger
from roster_sdk.client.agent import CollaborationInterface

from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import AgentAction, AgentFinish
from langchain.tools import StructuredTool

role_context_description = """
Get details about your current role on your team.
"""

team_context_description = """
Figure out who your teammates are and who your manager is.
Also displays role context for all members of your team.
"""

ask_team_member_description = """
Ask a question to a teammate using the name of their role.
"""

ask_manager_description = """
Ask a question to your manager.
"""


def async_structured_tool(
    func,
    description: str,
    **kwargs,
) -> StructuredTool:
    return StructuredTool.from_function(
        func,
        coroutine=func,
        description=description,
        **kwargs,
    )


def roster_collaboration_tools(team: str, role: str) -> list[StructuredTool]:
    collab_interface = CollaborationInterface(team=team, role=role)

    return [
        async_structured_tool(
            collab_interface.get_role_context,
            description=role_context_description,
        ),
        async_structured_tool(
            collab_interface.get_team_context,
            description=team_context_description,
        ),
        async_structured_tool(
            collab_interface.ask_team_member,
            description=ask_team_member_description,
        ),
        # async_structured_tool(
        #     collab_interface.ask_manager,
        #     description=ask_manager_description,
        # ),
    ]


def get_roster_langchain_tools(team: str, role: str) -> list[StructuredTool]:
    # Extend with additional interfaces
    return roster_collaboration_tools(team=team, role=role)


# It seems that langchain assumes the callback handler
# must be async if the agent is being run async
class RosterLoggingHandler(AsyncCallbackHandler):
    async def on_llm_start(
        self,
        serialized,
        prompts,
        *,
        run_id,
        parent_run_id=None,
        **kwargs,
    ) -> None:
        logger = get_logger()
        logger.debug(f"[LLM START] Prompts: {prompts}")

    async def on_llm_end(
        self,
        response,
        *,
        run_id,
        parent_run_id=None,
        **kwargs,
    ) -> None:
        logger = get_logger()
        logger.debug(f"[LLM END] Response: {response}")

    async def on_agent_action(
        self,
        action: AgentAction,
        *,
        run_id,
        parent_run_id=None,
        **kwargs,
    ) -> None:
        logger = get_roster_activity_logger()
        logger.action(action.log)

    async def on_tool_end(
        self,
        output: str,
        *,
        run_id,
        parent_run_id=None,
        tags=None,
        **kwargs,
    ) -> None:
        logger = get_roster_activity_logger()
        logger.action(f"Tool Output: {output}")

    async def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id,
        parent_run_id=None,
        **kwargs,
    ):
        logger = get_roster_activity_logger()
        logger.action(finish.log)
