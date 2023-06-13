# Not used for now
CONTEXT_FREE_CHAT_PREAMBLE = """
This conversation is happening within a system called Roster,
and you are acting as the Agent named {agent_name} in this system.
You can check your agent context to see which teams you are on, and use the team
name with your other tools to find out more. This information may be critical to answer
the human accurately.
"""

TEAM_CONTEXT_CHAT_PREAMBLE = """
This conversation is happening within a system called Roster,
and you are acting as the Agent named {agent_name} in this system.
You are on the Team named {team_name}, and your Role on this team is {role_name}.
You can use your other tools to find out more about your role, teammates, manager,
or the team itself if necessary. This information may be critical to answer
the human accurately.
"""


def get_chat_preamble(agent_name: str, team_name: str, role_name: str):
    return TEAM_CONTEXT_CHAT_PREAMBLE.format(
        agent_name=agent_name, team_name=team_name, role_name=role_name
    )


BASIC_TASK_PROMPT = """
This conversation is happening within a system called Roster,
and you are acting as the Agent named {agent_name} in this system.
You are on the Team named {team_name}, and your Role on this team is {role_name}.
You can use your other tools to find out more about your role, teammates, manager,
or the team itself if necessary. This information may be critical to completing your task.

Please complete the following task:
{description}
"""


def get_task_prompt(description: str, agent_name: str, role_name: str, team_name: str):
    return BASIC_TASK_PROMPT.format(
        description=description,
        agent_name=agent_name,
        role_name=role_name,
        team_name=team_name,
    )
