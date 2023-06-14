import inspect
from functools import wraps

from roster_sdk.agent.logs import get_roster_agent_logger
from roster_sdk.client.agent import CollaborationInterface

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
from langchain.tools import StructuredTool

role_context_description = """
Figure out more about your current role on your team.
"""

team_context_description = """
Figure out who your teammates are and who your manager is.
"""

ask_team_member_description = """
Ask a question to a teammate. Use the name of their role on the team.
"""

ask_manager_description = """
Ask a question to your manager.
"""


# TODO: async tools


def roster_collaboration_tools(team: str, role: str) -> list[StructuredTool]:
    collab_interface = CollaborationInterface(team=team, role=role)

    return [
        StructuredTool.from_function(
            collab_interface.get_role_context,
            description=role_context_description,
        ),
        StructuredTool.from_function(
            collab_interface.get_team_context,
            description=team_context_description,
        ),
        StructuredTool.from_function(
            collab_interface.ask_team_member,
            description=ask_team_member_description,
        ),
        StructuredTool.from_function(
            collab_interface.ask_manager,
            description=ask_manager_description,
        ),
    ]


def get_roster_langchain_tools(team: str, role: str) -> list[StructuredTool]:
    # Extend with additional interfaces
    return roster_collaboration_tools(team=team, role=role)


class RosterLoggingHandler(BaseCallbackHandler):
    def on_llm_start(
        self,
        serialized: dict,
        prompts: list[str],
        **kwargs,
    ) -> None:
        logger = get_roster_agent_logger()
        logger.info("[PROMPT LLM]")
        logger.info("\n".join(prompts))
        logger.info("[END PROMPT]")

    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        logger = get_roster_agent_logger()
        logger.info("[RESPONSE LLM]")
        logger.info(
            "\n".join(
                [
                    " ".join(map(lambda gen: gen.text, result))
                    for result in response.generations
                ]
            )
        )
        logger.info("[END RESPONSE]")
