from functools import cached_property
from typing import Generic, Type, TypeVar

import pydantic
import requests
from roster_sdk import config
from roster_sdk.client import errors
from roster_sdk.models.chat import ChatMessage
from roster_sdk.models.resources.agent import AgentResource
from roster_sdk.models.resources.role import RoleResource
from roster_sdk.models.resources.task import TaskResource
from roster_sdk.models.resources.team import TeamResource
from roster_sdk.models.resources.team_layout import TeamLayoutResource

ResourceType = TypeVar("ResourceType")


class CRUDResource(Generic[ResourceType]):
    def __init__(
        self, client: "RosterClient", endpoint: str, resource_type: Type[ResourceType]
    ):
        self.client = client
        self.endpoint = endpoint
        self.resource_type = resource_type

    def _deserialize(self, data: dict) -> ResourceType:
        try:
            return self.resource_type(**data)
        except TypeError:
            raise errors.RosterClientException(
                f"Expected {self.resource_type} but got {data}"
            )

    def create(self, data: dict) -> ResourceType:
        return self._deserialize(self.client.post(self.endpoint, data=data))

    def list(self) -> list[ResourceType]:
        return list(map(self._deserialize, self.client.get(self.endpoint)))

    def get(self, name: str) -> ResourceType:
        if not name:
            raise errors.RosterClientException("Cannot get resource with empty name.")
        return self._deserialize(self.client.get(f"{self.endpoint}/{name}"))

    def update(self, name: str, data: dict) -> ResourceType:
        if not name:
            raise errors.RosterClientException(
                "Cannot update resource with empty name."
            )
        return self._deserialize(
            self.client.patch(f"{self.endpoint}/{name}", data=data)
        )

    def delete(self, name: str) -> None:
        if not name:
            raise errors.RosterClientException(
                "Cannot delete resource with empty name."
            )
        self.client.delete(f"{self.endpoint}/{name}")


class RosterClient:
    def __init__(self, roster_api_url: str):
        self.roster_api_url = roster_api_url

    @classmethod
    def from_env(cls) -> "RosterClient":
        return cls(roster_api_url=config.ROSTER_API_URL)

    def _request(
        self, method: str, endpoint: str, data: dict = None
    ) -> requests.Response:
        try:
            response = requests.request(
                method=method, url=f"{self.roster_api_url}{endpoint}", json=data
            )
        except requests.exceptions.ConnectionError:
            raise errors.RosterConnectionError()
        if response.status_code == 404:
            raise errors.ResourceNotFound()
        elif response.status_code != 200:
            raise errors.RosterClientException(
                f"Roster API returned {response.status_code}"
            )
        return response

    def get(self, endpoint: str) -> dict:
        return self._request("GET", endpoint).json()

    def post(self, endpoint: str, data: dict) -> dict:
        return self._request("POST", endpoint, data=data).json()

    def patch(self, endpoint: str, data: dict) -> dict:
        return self._request("PATCH", endpoint, data=data).json()

    def delete(self, endpoint: str) -> None:
        self._request("DELETE", endpoint)

    def status_update(self, data: dict) -> None:
        self.post(config.ROSTER_API_STATUS_UPDATE_PATH, data=data)

    def chat_prompt_agent(
        self,
        agent: str,
        history: list[ChatMessage],
        message: ChatMessage,
        team: str = "",
    ) -> ChatMessage:
        try:
            response_data = self.post(
                f"{config.ROSTER_API_COMMANDS_PATH}/agent-chat/{agent}",
                data={
                    "history": [_message.dict() for _message in history],
                    "message": message.dict(),
                    "team": team,
                },
            )
            return ChatMessage(**response_data)
        except errors.RosterClientException:
            raise
        except pydantic.ValidationError as e:
            raise errors.RosterClientException(e.json())

    @cached_property
    def agent(self) -> CRUDResource[AgentResource]:
        return CRUDResource(
            client=self,
            endpoint=config.ROSTER_API_AGENTS_PATH,
            resource_type=AgentResource,
        )

    @cached_property
    def role(self) -> CRUDResource[RoleResource]:
        return CRUDResource(
            client=self,
            endpoint=config.ROSTER_API_ROLES_PATH,
            resource_type=RoleResource,
        )

    @cached_property
    def team(self) -> CRUDResource[TeamResource]:
        return CRUDResource(
            client=self,
            endpoint=config.ROSTER_API_TEAMS_PATH,
            resource_type=TeamResource,
        )

    @cached_property
    def team_layout(self) -> CRUDResource[TeamLayoutResource]:
        return CRUDResource(
            client=self,
            endpoint=config.ROSTER_API_TEAM_LAYOUTS_PATH,
            resource_type=TeamLayoutResource,
        )

    @cached_property
    def task(self) -> CRUDResource[TaskResource]:
        return CRUDResource(
            client=self,
            endpoint=config.ROSTER_API_TASKS_PATH,
            resource_type=TaskResource,
        )
