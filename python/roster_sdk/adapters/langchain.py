import asyncio
import os
import signal
from typing import TYPE_CHECKING, Callable

import websockets

from ..interface import RosterAgentInterface

if TYPE_CHECKING:
    from langchain.chains.base import Chain


loop = asyncio.get_event_loop()


class LangchainAgent(RosterAgentInterface):
    def __init__(self, chain: "Chain"):
        self.chain = chain
        self.conversation_server = None

    @property
    def conversation_message_handler(self) -> Callable:
        async def respond(websocket, path):
            async for message in websocket:
                if message == "end_conversation":
                    self.end_conversation()
                    return
                response = self.chain.run(message)
                await websocket.send(response)

        return respond

    def start_conversation(self, name: str) -> None:
        if self.conversation_server is not None:
            raise RuntimeError("Conversation server already running")
        port = os.environ.get("ROSTER_AGENT_CONVERSATION_PORT", 8765)
        start_server = websockets.serve(
            self.conversation_message_handler, "localhost", port
        )

        self.conversation_server = loop.run_until_complete(start_server)

        loop.add_signal_handler(signal.SIGINT, self.end_conversation)
        loop.add_signal_handler(signal.SIGTERM, self.end_conversation)
        loop.run_forever()

    def end_conversation(self) -> None:
        if self.conversation_server is None:
            raise RuntimeError("Conversation server not running")
        self.conversation_server.close()
        self.conversation_server = None
        loop.stop()

    def execute_task(self, name: str, description: str) -> None:
        """Execute a task on the agent"""
        self.chain.run(
            f"Please complete the following task:\nName: {name}\nDescription: {description}"
        )
