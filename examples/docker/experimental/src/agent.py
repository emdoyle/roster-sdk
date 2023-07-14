import guidance
from guidance.llms._openai import prompt_to_messages
from roster_sdk.agent.interface import BaseRosterAgent
from roster_sdk.models.chat import ChatMessage
from roster_sdk.models.resources.task import TaskAssignment

gpt = guidance.llms.OpenAI("gpt-3.5-turbo")


async def _patched_lib_call(**kwargs):
    print(
        f"LLM IN: {prompt_to_messages(kwargs['prompt']) if 'prompt' in kwargs else None}"
    )
    out = await guidance.llms.OpenAI._library_call(gpt, **kwargs)
    print(f"LLM OUT: {out}")
    return out


gpt.caller = _patched_lib_call

chat_program = guidance(
    """
{{#system~}}
You are a helpful assistant.
{{>tool_def functions=functions}}

This conversation is happening within a system called Roster,
and you are acting as the Agent named {{agent_name}} in this system.
You are on the Team named {{team_name}}, and your Role on this team is {{role_name}}.
You can use functions described above to find out more about your role, teammates, manager,
or the team itself if necessary. This information may be critical to answer
the human accurately.
{{~/system}}

{{#each messages}}
{{#if this.sender == agent_name}}
{{#assistant~}}{{this.sender}}: {{this.message}}{{~/assistant}}
{{else}}
{{#user~}}{{this.sender}}: {{this.message}}{{~/user}}
{{/if}}
{{/each}}
{{#assistant~}}{{gen 'answer' temperature=0.5 function_call='auto'}}{{~/assistant}}""",
    llm=gpt,
    async_mode=True,
    log=True,
)


class ExperimentalAgent(BaseRosterAgent):
    async def chat(
        self, identity: str, team: str, role: str, chat_history: list[ChatMessage]
    ) -> str:
        result = await chat_program(
            agent_name=identity,
            team_name=team,
            role_name=role,
            messages=chat_history,
            functions=[],
        )
        return result.get("answer", "Guidance failed to return a result.")

    async def execute_task(
        self, name: str, description: str, assignment: TaskAssignment
    ) -> str:
        ...


agent = ExperimentalAgent()
