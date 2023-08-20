from typing import Optional, TypeVar, Union

from roster_sdk.client import errors
from roster_sdk.client.base import RosterClient
from roster_sdk.models.chat import ChatMessage
from roster_sdk.models.client.role import RoleContext

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

    async def ask_team_member(
        self, member_role: str, question: str
    ) -> Result[ChatMessage]:
        try:
            team_resource = await self.client.team.get(self.team)
        except errors.RosterClientException:
            return "Team not found."

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
