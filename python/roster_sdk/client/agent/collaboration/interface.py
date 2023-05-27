from roster_sdk.client.base import RosterClient


class RosterAgentCollaborationInterface:
    def __init__(self, agent_name: str, client: RosterClient):
        self.agent_name = agent_name
        self.client = client

    @classmethod
    def from_env(cls, agent_name: str) -> "RosterAgentCollaborationInterface":
        return cls(agent_name, RosterClient.from_env())

    async def get_role_context(self, team: str) -> dict:
        pass

    async def get_team_context(self, team: str) -> dict:
        pass

    async def get_team_members(self, team: str) -> list[str]:
        pass

    async def ask_team_member(self, team: str, peer: str, question: str) -> str:
        pass

    async def ask_manager(self, question: str) -> str:
        pass
