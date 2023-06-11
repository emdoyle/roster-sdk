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
You are on the Team named {team_name}, and you can use this team name
with your other tools to find out more about your role, teammates, manager,
or the team itself if necessary. This information may be critical to answer
the human accurately.
"""


def get_chat_preamble(agent_name: str, team_name: str = ""):
    if team_name:
        return TEAM_CONTEXT_CHAT_PREAMBLE.format(
            agent_name=agent_name, team_name=team_name
        )
    return CONTEXT_FREE_CHAT_PREAMBLE.format(agent_name=agent_name)


BASIC_TASK_PROMPT = """
Please complete the following task:
{description}

The task should be done in the context of your role as {role_name} in the team {team_name}.
Use this team name with your other tools to get more context about your team, teammates, role,
or manager if necessary.
"""


def get_task_prompt(description: str, role_name: str, team_name: str):
    return BASIC_TASK_PROMPT.format(
        description=description, role_name=role_name, team_name=team_name
    )
