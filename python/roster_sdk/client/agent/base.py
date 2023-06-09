from roster_sdk.client.base import RosterClient
from roster_sdk.models.client.agent import AgentContext


class BaseRosterInterface:
    def __init__(self, agent_name: str, client: RosterClient):
        self.agent_name = agent_name
        self.client = client

    @classmethod
    def from_env(cls, agent_name: str) -> "BaseRosterInterface":
        return cls(agent_name, RosterClient.from_env())

    def get_agent_context(self) -> AgentContext:
        teams = self.client.team.list()
        agent_teams = [
            team.spec.name
            for team in teams
            if team.get_agent_role(self.agent_name) is not None
        ]
        return AgentContext(name=self.agent_name, teams=agent_teams)
