CHAT_PREAMBLE = """
Before giving up, use a tool to check your agent context, and then your role context on your team.
Please respond to what I say next: """

BASIC_TASK_PROMPT = """
Please complete the following task:
{description}

The task should be done in the context of your role as {role_name} in the team {team_name}.
Use tools to get more context about your team, teammates, role, or manager if necessary.
"""
