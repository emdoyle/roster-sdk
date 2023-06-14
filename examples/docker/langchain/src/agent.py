from langchain.agents import AgentType, initialize_agent
from langchain.agents.structured_chat.prompt import SUFFIX as STRUCTURED_CHAT_SUFFIX
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage as BaseLangchainMessage
from langchain.schema import HumanMessage
from roster_sdk.adapters import get_roster_langchain_tools
from roster_sdk.adapters.langchain import RosterLoggingHandler
from roster_sdk.adapters.prompts import get_chat_preamble, get_task_prompt
from roster_sdk.agent.interface import BaseRosterAgent
from roster_sdk.models.chat import ChatMessage
from roster_sdk.models.resources.task import TaskAssignment


def basic_chat_agent(team: str, role: str, **agent_kwargs):
    return initialize_agent(
        get_roster_langchain_tools(team=team, role=role),
        ChatOpenAI(temperature=0),
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_kwargs=agent_kwargs,
    )


class LangchainAgent(BaseRosterAgent):
    @classmethod
    def _ai_message(cls, message: ChatMessage) -> BaseLangchainMessage:
        class _AIMessage(BaseLangchainMessage):
            example: bool = False

            @property
            def type(self) -> str:
                """Type of the message, used for serialization."""
                return message.sender

        return _AIMessage(content=message.message)

    async def chat(
        self, identity: str, team: str, role: str, chat_history: list[ChatMessage]
    ) -> str:
        memory = [
            self._ai_message(message)
            if message.sender == identity
            else HumanMessage(content=message.message)
            for message in chat_history[:-1]
        ]
        suffix = (
            get_chat_preamble(agent_name=identity, team_name=team, role_name=role)
            + STRUCTURED_CHAT_SUFFIX
        )
        return basic_chat_agent(
            team=team, role=role, memory_prompts=memory, suffix=suffix
        ).run(
            chat_history[-1].message,
            callbacks=[RosterLoggingHandler()],
        )

    async def execute_task(
        self, name: str, description: str, assignment: TaskAssignment
    ) -> str:
        # NOTE: Agent does not know the name of the Task
        # (caused confusion in GPT-3.5 testing, and is pretty much metadata anyway)
        task_message = get_task_prompt(
            description=description,
            agent_name=assignment.identity_name,
            role_name=assignment.role_name,
            team_name=assignment.team_name,
        )
        return basic_chat_agent(
            team=assignment.team_name, role=assignment.role_name
        ).run(task_message, callbacks=[RosterLoggingHandler()])


agent = LangchainAgent()
