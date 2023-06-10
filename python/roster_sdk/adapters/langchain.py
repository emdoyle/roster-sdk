from functools import wraps

from roster_sdk.agent.logs import get_roster_agent_logger
from roster_sdk.client.agent import CollaborationInterface
from roster_sdk.client.agent.base import BaseRosterInterface
from roster_sdk.config import AgentConfig

from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import LLMResult
from langchain.tools import StructuredTool

agent_context_description = """
Figure out your name and what teams you're on.
"""

role_context_description = """
Figure out what your current role is on a given team.
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


def strfn(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return str(fn(*args, **kwargs))

    return wrapper


def roster_base_tools(agent: str) -> list[StructuredTool]:
    base_interface = BaseRosterInterface.from_env(agent_name=agent)
    return [
        StructuredTool.from_function(
            strfn(base_interface.get_agent_context),
            description=agent_context_description,
        ),
    ]


# TODO: async tools


def roster_collaboration_tools(agent: str) -> list[StructuredTool]:
    collab_interface = CollaborationInterface.from_env(agent_name=agent)
    return [
        StructuredTool.from_function(
            strfn(collab_interface.get_role_context),
            description=role_context_description,
        ),
        StructuredTool.from_function(
            strfn(collab_interface.get_team_context),
            description=team_context_description,
        ),
        StructuredTool.from_function(
            strfn(collab_interface.ask_team_member),
            description=ask_team_member_description,
        ),
        StructuredTool.from_function(
            strfn(collab_interface.ask_manager), description=ask_manager_description
        ),
    ]


def get_roster_langchain_tools() -> list[StructuredTool]:
    agent = AgentConfig.from_env().roster_agent_name
    return [*roster_base_tools(agent), *roster_collaboration_tools(agent)]


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
