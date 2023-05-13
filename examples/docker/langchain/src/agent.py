import roster_sdk

from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory


def basic_chat_agent():
    return initialize_agent(
        [],
        ChatOpenAI(temperature=0),
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=True,
        memory=ConversationBufferMemory(
            memory_key="chat_history", return_messages=True
        ),
    )


agent = roster_sdk.LangchainAgent(basic_chat_agent())
