from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from roster_sdk.adapters import get_roster_langchain_tools
from roster_sdk.agent.interface import BaseRosterAgent
from roster_sdk.models.chat import ChatMessage


def basic_chat_agent():
    return initialize_agent(
        get_roster_langchain_tools(),
        ChatOpenAI(temperature=0),
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )


class LangchainAgent(BaseRosterAgent):
    def __init__(self):
        super().__init__()
        self.agent = basic_chat_agent()

    async def chat(self, chat_history: list[ChatMessage]) -> str:
        return self.agent.run(chat_history[-1].message)

    async def execute_task(self, name: str, description: str) -> None:
        ...


agent = LangchainAgent()
