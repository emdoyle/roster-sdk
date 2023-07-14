import asyncio

from roster_sdk.models.chat import ChatMessage

from src.agent import ExperimentalAgent

msg = ChatMessage(sender="Evan", message="What is your name?")

ea = ExperimentalAgent()

result = asyncio.run(ea.chat("David", "Alpha Team", "Member", [msg]))

print(f"Result is {result}")
