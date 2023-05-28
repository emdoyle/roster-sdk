from roster_sdk.client.base import RosterClient
from roster_sdk.models.client.role import RoleContext
from roster_sdk.models.client.team import TeamContext, TeamLayoutContext


class RosterAgentCollaborationInterface:
    def __init__(self, agent_name: str, client: RosterClient):
        self.agent_name = agent_name
        self.client = client

    @classmethod
    def from_env(cls, agent_name: str) -> "RosterAgentCollaborationInterface":
        return cls(agent_name, RosterClient.from_env())

    def get_role_context(self, team: str) -> RoleContext:
        team_resource = self.client.team.get(team)
        role_spec = team_resource.get_agent_role(self.agent_name)
        return RoleContext(
            team=team, role=role_spec.name, description=role_spec.description
        )

    def get_team_context(self, team: str) -> TeamContext:
        team_resource = self.client.team.get(team)
        return TeamContext(
            name=team_resource.spec.name,
            layout=TeamLayoutContext(
                roles={
                    role_name: RoleContext(
                        team=team,
                        role=role_name,
                        description=role_spec.description,
                    )
                    for role_name, role_spec in team_resource.spec.layout.roles
                },
                peer_groups=team_resource.spec.layout.peer_groups,
                management_groups=team_resource.spec.layout.management_groups,
            ),
        )

    def ask_team_member(self, team: str, peer: str, question: str) -> str:
        pass

    def ask_manager(self, question: str) -> str:
        pass
