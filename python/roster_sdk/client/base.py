from functools import cached_property
from typing import Generic, Type, TypeVar

import aiohttp
import pydantic
from roster_sdk import config
from roster_sdk.agent.context import get_agent_activity_context
from roster_sdk.client import errors
from roster_sdk.constants import EXECUTION_ID_HEADER, EXECUTION_TYPE_HEADER
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

    async def create(self, data: dict) -> ResourceType:
        return self._deserialize(await self.client.post(self.endpoint, data=data))

    async def list(self) -> list[ResourceType]:
        return list(map(self._deserialize, await self.client.get(self.endpoint)))

    async def get(self, name: str) -> ResourceType:
        if not name:
            raise errors.RosterClientException("Cannot get resource with empty name.")
        return self._deserialize(await self.client.get(f"{self.endpoint}/{name}"))

    async def update(self, name: str, data: dict) -> ResourceType:
        if not name:
            raise errors.RosterClientException(
                "Cannot update resource with empty name."
            )
        return self._deserialize(
            await self.client.patch(f"{self.endpoint}/{name}", data=data)
        )

    async def delete(self, name: str) -> None:
        if not name:
            raise errors.RosterClientException(
                "Cannot delete resource with empty name."
            )
        await self.client.delete(f"{self.endpoint}/{name}")


class RosterClient:
    def __init__(self, roster_api_url: str):
        self.roster_api_url = roster_api_url

    @classmethod
    def from_env(cls) -> "RosterClient":
        return cls(roster_api_url=config.ROSTER_API_URL)

    async def _request(self, method: str, endpoint: str, data: dict = None) -> dict:
        async with aiohttp.ClientSession() as session:
            try:
                activity_context = get_agent_activity_context()
                if activity_context:
                    _, execution_ctx = activity_context
                    headers = {
                        EXECUTION_ID_HEADER: execution_ctx.execution_id,
                        EXECUTION_TYPE_HEADER: execution_ctx.execution_type,
                    }
                else:
                    headers = None
                async with session.request(
                    method=method,
                    url=f"{self.roster_api_url}{endpoint}",
                    json=data,
                    headers=headers,
                ) as response:
                    if response.status == 404:
                        raise errors.ResourceNotFound()
                    elif response.status != 200:
                        raise errors.RosterClientException(
                            f"Roster API returned {response.status}"
                        )
                    return await response.json()
            except aiohttp.ClientConnectionError:
                raise errors.RosterConnectionError()

    async def get(self, endpoint: str) -> dict:
        return await self._request("GET", endpoint)

    async def post(self, endpoint: str, data: dict) -> dict:
        return await self._request("POST", endpoint, data=data)

    async def patch(self, endpoint: str, data: dict) -> dict:
        return await self._request("PATCH", endpoint, data=data)

    async def delete(self, endpoint: str) -> None:
        await self._request("DELETE", endpoint)

    async def status_update(self, data: dict) -> None:
        await self.post(config.ROSTER_API_STATUS_UPDATE_PATH, data=data)

    async def chat_prompt_agent(
        self,
        role: str,
        team: str,
        history: list[ChatMessage],
        message: ChatMessage,
    ) -> ChatMessage:
        try:
            response_data = await self.post(
                f"{config.ROSTER_API_COMMANDS_PATH}/agent-chat",
                data={
                    "team": team,
                    "role": role,
                    "history": [_message.dict() for _message in history],
                    "message": message.dict(),
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
