from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage as BaseLangchainMessage
from langchain.schema import HumanMessage, SystemMessage
from roster_sdk.adapters import get_roster_langchain_tools
from roster_sdk.adapters.langchain import RosterLoggingHandler
from roster_sdk.adapters.prompts import get_roster_preamble
from roster_sdk.agent.interface import BaseRosterAgent
from roster_sdk.models.chat import ChatMessage
from roster_sdk.models.resources.task import TaskAssignment


def build_agent(
    team: str,
    role: str,
    temperature: float = 0,
    model: str = "gpt-4",
    **agent_kwargs,
):
    return initialize_agent(
        get_roster_langchain_tools(team=team, role=role),
        ChatOpenAI(temperature=temperature, model_name=model),
        agent=AgentType.OPENAI_FUNCTIONS,
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
        system_message = SystemMessage(
            content=get_roster_preamble(
                agent_name=identity, team_name=team, role_name=role
            )
        )

        memory = []
        for message in chat_history[:-1]:
            if message.sender == identity:
                memory.append(self._ai_message(message))
            else:
                memory.append(HumanMessage(content=message.message))

        return await build_agent(
            team=team,
            role=role,
            system_message=system_message,
            extra_prompt_messages=memory,
        ).arun(
            chat_history[-1].message,
            callbacks=[RosterLoggingHandler()],
        )

    async def execute_task(
        self, name: str, description: str, assignment: TaskAssignment
    ) -> str:
        # NOTE: Agent does not know the name of the Task
        # (caused confusion in GPT-3.5 testing, and is pretty much metadata anyway)
        system_message = SystemMessage(
            content=get_roster_preamble(
                agent_name=assignment.identity_name,
                role_name=assignment.role_name,
                team_name=assignment.team_name,
            )
        )

        task_message = f"Please complete the following task:\n{description}"

        return await build_agent(
            team=assignment.team_name,
            role=assignment.role_name,
            system_message=system_message,
        ).arun(task_message, callbacks=[RosterLoggingHandler()])


agent = LangchainAgent()
