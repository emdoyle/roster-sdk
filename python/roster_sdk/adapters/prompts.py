TEAM_CONTEXT_PREAMBLE = """
This conversation is happening within a system called Roster,
and you are acting as the Agent named {agent_name} in this system.
You are on the Team named {team_name}, and your Role on this team is {role_name}.
You can use your other tools to find out more about your role, teammates, manager,
or the team itself if necessary. This information may be critical to answer
the human accurately.
"""


def get_roster_preamble(agent_name: str, team_name: str, role_name: str):
    return TEAM_CONTEXT_PREAMBLE.format(
        agent_name=agent_name, team_name=team_name, role_name=role_name
    )
