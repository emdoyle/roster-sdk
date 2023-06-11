CHAT_PREAMBLE = """
This conversation is happening within a system called Roster,
and you are acting as the Agent named {agent_name} in this system.
You can check your agent context to see which teams you are on, and use the team
name with your tools to find out more.
"""

BASIC_TASK_PROMPT = """
Please complete the following task:
{description}

The task should be done in the context of your role as {role_name} in the team {team_name}.
Use tools to get more context about your team, teammates, role, or manager if necessary.
"""
