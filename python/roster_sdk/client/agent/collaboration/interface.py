from roster_sdk.client import errors
from roster_sdk.client.base import RosterClient
from roster_sdk.models.chat import ChatMessage
from roster_sdk.models.client.role import RoleContext
from roster_sdk.models.client.team import TeamContext


class CollaborationInterface:
    def __init__(self, agent_name: str, client: RosterClient):
        self.agent_name = agent_name
        self.client = client

    @classmethod
    def from_env(cls, agent_name: str) -> "CollaborationInterface":
        return cls(agent_name, RosterClient.from_env())

    def get_role_context(self, team: str) -> RoleContext:
        team_resource = self.client.team.get(team)
        role_spec = team_resource.get_agent_role(self.agent_name)
        return RoleContext.from_spec(team, role_spec)

    def get_team_context(self, team: str) -> TeamContext:
        team_resource = self.client.team.get(team)
        return TeamContext.from_spec(self.agent_name, team_resource.spec)

    def ask_team_member(
        self, team: str, member_role: str, question: str
    ) -> ChatMessage:
        team_resource = self.client.team.get(team)
        # Check if member_role refers to a role on the team.
        member = team_resource.get_member_by_role(member_role)
        if member is None:
            raise errors.TeamMemberNotFound()
        # Check if the member_role is in the agent's peer group.
        agent_role = team_resource.get_agent_role(self.agent_name)
        if not team_resource.roles_share_peer_group(agent_role.name, member_role):
            raise errors.TeamMemberNotInPeerGroup()

        return self.client.chat_prompt_agent(
            member.name,
            history=[],
            message=ChatMessage(sender=self.agent_name, message=question),
        )

    def ask_manager(self, team: str, question: str) -> ChatMessage:
        team_resource = self.client.team.get(team)
        manager = team_resource.get_agent_manager(self.agent_name)
        if manager is None:
            raise errors.TeamMemberNotFound("Could not find manager for agent.")

        return self.client.chat_prompt_agent(
            manager.name,
            history=[],
            message=ChatMessage(sender=self.agent_name, message=question),
        )
