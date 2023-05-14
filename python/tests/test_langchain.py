import asyncio
import os
import signal
from multiprocessing import Process

import aiohttp
import pytest
import roster_sdk
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from roster_sdk.models.chat import ChatMessage

TESTING_CONVERSATION_PORT = 8765
TESTING_AGENT_NAME = "Alice"


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


@pytest.fixture
def process_manager():
    processes = []

    def run_in_process(target, *args, **kwargs):
        proc = Process(target=target, args=args, kwargs=kwargs)
        proc.start()
        processes.append(proc)
        return proc

    yield run_in_process

    for process in processes:
        try:
            if process.is_alive():
                os.kill(process.pid, signal.SIGTERM)
                process.join()
        except Exception:
            print(f"Failed to kill process {process.pid}")


@pytest.mark.asyncio
async def test_chat():
    agent = basic_chat_agent()
    roster_agent = roster_sdk.LangchainAgent(agent)
    response = await roster_agent.chat(
        [ChatMessage(sender="User", message="Hello, what is your name?")]
    )
    assert "Assistant" in response


def run_conversation_via_entrypoint():
    agent = basic_chat_agent()
    roster_agent = roster_sdk.LangchainAgent(agent)
    entrypoint = roster_sdk.Entrypoint(
        roster_agent,
        roster_sdk.Config(
            roster_runtime_ip="fake",
            roster_agent_name=TESTING_AGENT_NAME,
            roster_agent_port=TESTING_CONVERSATION_PORT,
        ),
    )
    entrypoint.run()


@pytest.mark.asyncio
async def test_entrypoint(process_manager):
    process_manager(target=run_conversation_via_entrypoint)
    await asyncio.sleep(5)
    url = f"http://localhost:{TESTING_CONVERSATION_PORT}"

    payload = [{"sender": "User", "message": "Hello, what is your name?"}]
    """make async http post request to the chat endpoint with payload"""
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{url}/chat", json=payload) as response:
            assert response.status == 200
            response = await response.json()
            assert response["sender"] == TESTING_AGENT_NAME
            assert "Assistant" in response["message"]
