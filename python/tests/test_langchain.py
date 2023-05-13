import asyncio
import os
import signal
from multiprocessing import Process

import pytest
import roster_sdk
import websockets
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory

TESTING_CONVERSATION_PORT = 8765


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


def run_conversation_server(name: str = "dinosaurs"):
    agent = basic_chat_agent()
    roster_agent = roster_sdk.LangchainAgent(agent)
    roster_agent.start_conversation(name, port=TESTING_CONVERSATION_PORT)


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
async def test_server(process_manager):
    server_process = process_manager(target=run_conversation_server)

    uri = f"ws://localhost:{TESTING_CONVERSATION_PORT}"

    async for websocket in websockets.connect(uri):
        await websocket.send("Hello, what is your name?")

        response = await websocket.recv()
        assert "Assistant" in response

        await websocket.send("end_conversation")
        break

    # Wait for the server to stop
    await asyncio.sleep(1)

    # Make sure the server process has ended
    assert not server_process.is_alive()


def run_conversation_via_entrypoint(name: str = "dinosaurs"):
    agent = basic_chat_agent()
    roster_agent = roster_sdk.LangchainAgent(agent)
    entrypoint = roster_sdk.Entrypoint(
        roster_agent,
        roster_sdk.Config(roster_agent_name="test", conversation_name=name),
    )
    entrypoint.run()


@pytest.mark.asyncio
async def test_entrypoint(process_manager):
    server_process = process_manager(target=run_conversation_via_entrypoint)

    uri = f"ws://localhost:{TESTING_CONVERSATION_PORT}"

    async for websocket in websockets.connect(uri):
        await websocket.send("Hello, what is your name?")

        response = await websocket.recv()
        assert "Assistant" in response

        await websocket.send("end_conversation")
        break

    # Wait for the server to stop
    await asyncio.sleep(1)

    # Make sure the server process has ended
    assert not server_process.is_alive()
