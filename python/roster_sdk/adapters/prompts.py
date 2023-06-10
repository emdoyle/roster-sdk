CHAT_PREAMBLE = """You are running in a collaboration system called Roster.
You may be asked to answer questions in the context of your role in a team.
If the you are referred to by a name you don't recognize, try checking your
role context with the `get_role_context` tool. Please respond to what I say below:

"""

BASIC_TASK_PROMPT = """
Please complete the following task:
{description}

The task should be done in the context of your role as {role_name} in the team {team_name}.
Use tools to get more context about your team, teammates, role, or manager if necessary.
"""
