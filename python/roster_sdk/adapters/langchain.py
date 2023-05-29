from functools import wraps

from roster_sdk.client.agent import CollaborationInterface
from roster_sdk.config import AgentConfig

from langchain.tools import StructuredTool

role_context_description = """
Figure out what your current role is on a given team.
Example:
role_context("Alpha Team") -> "team": "Alpha Team", "role": "Backend Python Developer", "description": ...
"""

team_context_description = """
Figure out who your teammates are and who your manager is.
Example:
team_context("Alpha Team") -> "team": "Alpha Team", "role": "Backend Python Developer", "peers": [...], "manager": ...
"""

ask_team_member_description = """
Ask a question to a teammate. Use the name of their role on the team.
Example:
ask_team_member("Alpha Team", "Frontend Developer", "What's the status of the new feature?") -> "It's almost done!"
"""

ask_manager_description = """
Ask a question to your manager.
Example:
ask_manager("Alpha Team", "What do you think of my work so far?") -> "It looks great!"
"""


def strfn(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        return str(fn(*args, **kwargs))

    return wrapper


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
    return [*roster_collaboration_tools(agent)]
