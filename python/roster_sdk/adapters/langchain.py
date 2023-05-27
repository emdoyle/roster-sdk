from typing import TYPE_CHECKING

from roster_sdk.agent.interface import RosterAgentInterface

from ..models.chat import ChatMessage

if TYPE_CHECKING:
    from langchain.chains.base import Chain


class LangchainAgent(RosterAgentInterface):
    def __init__(self, chain: "Chain"):
        self.chain = chain

    async def chat(self, chat_history: list[ChatMessage]) -> str:
        # If the Chain is a ConversationalAgent,
        # then it is already storing the history in a ConversationBufferMemory
        # so we should only send the last message
        return await self.chain.arun(chat_history[-1].message)

    async def execute_task(self, name: str, description: str) -> None:
        """Execute a task on the agent"""
        # TODO: The treatment of tasks depends on how we handle and store outputs/results
        #   this is just a single call to the Chain, but a task likely implies many calls
        #   and honestly it's usually controlled beneath this layer
        #   probably implies a more sophisticated interface
        #   most straightforward is for the ARI to provide the desired location for outputs
        #   and then the agent can write to that location
        await self.chain.arun(
            f"Please complete the following task:\nName: {name}\nDescription: {description}"
        )
