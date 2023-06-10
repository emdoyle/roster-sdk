from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from roster_sdk.adapters import get_roster_langchain_tools
from roster_sdk.adapters.langchain import RosterLoggingHandler
from roster_sdk.adapters.prompts import BASIC_TASK_PROMPT, CHAT_PREAMBLE
from roster_sdk.agent.interface import BaseRosterAgent
from roster_sdk.models.chat import ChatMessage
from roster_sdk.models.resources.task import TaskAssignment


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
        # NOTE: sort of depends on the agent not having memory
        self.agent = basic_chat_agent()

    async def chat(self, chat_history: list[ChatMessage]) -> str:
        return self.agent.run(
            CHAT_PREAMBLE + chat_history[-1].message, callbacks=[RosterLoggingHandler()]
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
        return self.agent.run(task_message, callbacks=[RosterLoggingHandler()])


agent = LangchainAgent()
