from typing import TypeVar, Union

from roster_sdk.client import errors
from roster_sdk.client.base import RosterClient
from roster_sdk.models.chat import ChatMessage
from roster_sdk.models.client.role import RoleContext
from roster_sdk.models.client.team import TeamContext

T = TypeVar("T")

# A bit strange, but since this interface is for text I/O based Agents,
# we can use a string to represent an error message.
Result = Union[str, T]


class CollaborationInterface:
    def __init__(self, agent_name: str, client: RosterClient):
        self.agent_name = agent_name
        self.client = client

    @classmethod
    def from_env(cls, agent_name: str) -> "CollaborationInterface":
        return cls(agent_name, RosterClient.from_env())

    def get_role_context(self, team: str) -> Result[RoleContext]:
        try:
            team_resource = self.client.team.get(team)
        except errors.RosterClientException:
            return "Team not found."
        role_spec = team_resource.get_agent_role(self.agent_name)
        return RoleContext.from_spec(team, role_spec)

    def get_team_context(self, team: str) -> Result[TeamContext]:
        try:
            team_resource = self.client.team.get(team)
        except errors.RosterClientException:
            return "Team not found."
        return TeamContext.from_spec(self.agent_name, team_resource.spec)

    def ask_team_member(
        self, team: str, member_role: str, question: str
    ) -> Result[ChatMessage]:
        try:
            team_resource = self.client.team.get(team)
        except errors.RosterClientException:
            return "Team not found."
        # Check if member_role refers to a role on the team.
        member = team_resource.get_member_by_role(member_role)
        if member is None:
            return "Team member not found."
        # Check if the member_role is in the agent's peer group.
        agent_role = team_resource.get_agent_role(self.agent_name)
        if not team_resource.roles_share_peer_group(agent_role.name, member_role):
            return "Team member not in peer group."

        try:
            return self.client.chat_prompt_agent(
                member.name,
                history=[],
                message=ChatMessage(sender=self.agent_name, message=question),
            )
        except errors.RosterClientException:
            return "Failed to send message to team member."

    def ask_manager(self, team: str, question: str) -> Result[ChatMessage]:
        try:
            team_resource = self.client.team.get(team)
        except errors.RosterClientException:
            return "Team not found."
        manager = team_resource.get_agent_manager(self.agent_name)
        if manager is None:
            return "Could not find manager for agent."

        try:
            return self.client.chat_prompt_agent(
                manager.name,
                history=[],
                message=ChatMessage(sender=self.agent_name, message=question),
            )
        except errors.RosterClientException:
            return "Failed to send message to manager."
