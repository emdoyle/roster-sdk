import asyncio
import signal
from typing import TYPE_CHECKING, Callable, Optional

import websockets

from ..interface import RosterAgentInterface

if TYPE_CHECKING:
    from langchain.chains.base import Chain


loop = asyncio.get_event_loop()


class LangchainAgent(RosterAgentInterface):
    DEFAULT_CONVERSATION_PORT = 8765

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

    def start_conversation(self, name: str, port: Optional[int] = None) -> None:
        if self.conversation_server is not None:
            raise RuntimeError("Conversation server already running")
        port = port or self.DEFAULT_CONVERSATION_PORT
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
        # TODO: The treatment of tasks depends on how we handle and store outputs/results
        #   this is just a single call to the Chain, but a task likely implies many calls
        #   and honestly it's usually controlled beneath this layer
        #   probably implies a more sophisticated interface
        #   most straightforward is for the ARI to provide the desired location for outputs
        #   and then the agent can write to that location
        self.chain.run(
            f"Please complete the following task:\nName: {name}\nDescription: {description}"
        )
