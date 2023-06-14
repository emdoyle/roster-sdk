from typing import Optional, TypeVar, Union

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
    def __init__(self, team: str, role: str, client: Optional[RosterClient] = None):
        self.team = team
        self.role = role
        self.client = client or RosterClient.from_env()

    async def get_role_context(self) -> Result[RoleContext]:
        try:
            team_resource = await self.client.team.get(self.team)
        except errors.RosterClientException:
            return "Team not found."
        role = team_resource.get_role(self.role)
        if role is None:
            return "Role not found."
        return RoleContext.from_role(
            team_name=self.team, role_name=self.role, role=role
        )

    async def get_team_context(self) -> Result[TeamContext]:
        try:
            team_resource = await self.client.team.get(self.team)
        except errors.RosterClientException:
            return "Team not found."
        try:
            return TeamContext.from_resource(
                role_name=self.role, team_name=self.team, team_resource=team_resource
            )
        except errors.TeamMemberNotFound:
            return "Role not found."

    async def ask_team_member(
        self, member_role: str, question: str
    ) -> Result[ChatMessage]:
        try:
            team_resource = await self.client.team.get(self.team)
        except errors.RosterClientException:
            return "Team not found."

        # Check if the member_role is in the agent's peer group.
        if not team_resource.roles_share_peer_group(self.role, member_role):
            return "Team member not in peer group."

        agent_identity = team_resource.get_member_by_role(self.role)
        if agent_identity is None:
            return "Agent not found."

        try:
            return await self.client.chat_prompt_agent(
                role=member_role,
                team=self.team,
                history=[],
                message=ChatMessage(sender=agent_identity.identity, message=question),
            )
        except errors.RosterClientException:
            return "Failed to send message to team member."

    async def ask_manager(self, question: str) -> Result[ChatMessage]:
        try:
            team_resource = await self.client.team.get(self.team)
        except errors.RosterClientException:
            return "Team not found."
        manager = team_resource.get_role_manager(self.role)
        if manager is None:
            return "Could not find manager for agent."

        agent_identity = team_resource.get_member_by_role(self.role)
        if agent_identity is None:
            return "Agent not found."

        try:
            return await self.client.chat_prompt_agent(
                role=manager,
                team=self.team,
                history=[],
                message=ChatMessage(sender=agent_identity.identity, message=question),
            )
        except errors.RosterClientException:
            return "Failed to send message to manager."
