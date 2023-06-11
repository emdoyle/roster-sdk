from langchain.agents import AgentType, initialize_agent
from langchain.agents.structured_chat.prompt import SUFFIX as STRUCTURED_CHAT_SUFFIX
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage
from langchain.schema import BaseMessage as BaseLangchainMessage
from langchain.schema import HumanMessage
from roster_sdk.adapters import get_roster_langchain_tools
from roster_sdk.adapters.langchain import RosterLoggingHandler
from roster_sdk.adapters.prompts import BASIC_TASK_PROMPT, CHAT_PREAMBLE
from roster_sdk.agent.interface import BaseRosterAgent
from roster_sdk.models.chat import ChatMessage
from roster_sdk.models.resources.task import TaskAssignment


def basic_chat_agent(**agent_kwargs):
    return initialize_agent(
        get_roster_langchain_tools(),
        ChatOpenAI(temperature=0),
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs=agent_kwargs,
    )


class LangchainAgent(BaseRosterAgent):
    def _adapt_chat_message(self, chat: ChatMessage) -> BaseLangchainMessage:
        if chat.sender == self.agent_name:
            return AIMessage(content=chat.message)
        else:
            return HumanMessage(content=chat.message)

    async def chat(self, chat_history: list[ChatMessage]) -> str:
        memory = list(map(self._adapt_chat_message, chat_history[:-1]))
        suffix = (
            CHAT_PREAMBLE.format(agent_name=self.agent_name) + STRUCTURED_CHAT_SUFFIX
        )
        return basic_chat_agent(memory_prompts=memory, suffix=suffix).run(
            chat_history[-1].message,
            callbacks=[RosterLoggingHandler()],
        )

    async def execute_task(
        self, name: str, description: str, assignment: TaskAssignment
    ) -> str:
        task_message = BASIC_TASK_PROMPT.format(
            name=name,
            description=description,
            role_name=assignment.role_name,
            team_name=assignment.team_name,
        )
        return basic_chat_agent().run(task_message, callbacks=[RosterLoggingHandler()])


agent = LangchainAgent()
