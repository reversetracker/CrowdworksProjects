import json
from json import JSONDecodeError
from typing import List, Union

from langchain.agents.agent import MultiActionAgentOutputParser
from langchain_core.agents import AgentAction, AgentActionMessageLog, AgentFinish
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
)
from langchain_core.outputs import ChatGeneration, Generation


class HyperclovaAgentAction(AgentActionMessageLog):
    tool_call_id: str
    """Tool call that this message is responding to."""


def parse_ai_message_to_hyperclova_action(
    message: BaseMessage,
) -> Union[List[AgentAction], AgentFinish]:
    """Parse an AI message potentially containing tool_calls."""
    if not isinstance(message, AIMessage):
        raise TypeError(f"Expected an AI message got {type(message)}")

    if not message.additional_kwargs.get("tool_calls"):
        return AgentFinish(
            return_values={"output": message.content}, log=str(message.content)
        )

    actions: List = []
    for tool_call in message.additional_kwargs["tool_calls"]:
        function = tool_call["function"]
        function_name = function["name"]
        try:
            _tool_input = json.loads(function["arguments"] or "{}")
        except JSONDecodeError:
            raise OutputParserException(
                f"Could not parse tool input: {function} because "
                f"the `arguments` is not valid JSON."
            )

        # HACK HACK HACK:
        # The code that encodes tool input into Open AI uses a special variable
        # name called `__arg1` to handle old style tools that do not expose a
        # schema and expect a single string argument as an input.
        # We unpack the argument here if it exists.
        # Open AI does not support passing in a JSON array as an argument.
        if "__arg1" in _tool_input:
            tool_input = _tool_input["__arg1"]
        else:
            tool_input = _tool_input

        content_msg = f"responded: {message.content}\n" if message.content else "\n"
        log = f"\nInvoking: `{function_name}` with `{tool_input}`\n{content_msg}\n"
        actions.append(
            HyperclovaAgentAction(
                tool=function_name,
                tool_input=tool_input,
                log=log,
                message_log=[message],
                tool_call_id=tool_call["id"],
            )
        )
    return actions


class HyperclovaAgentOutputParser(MultiActionAgentOutputParser):

    @property
    def _type(self) -> str:
        return "hyperclova-agent-output-parser"

    def parse_result(
        self, result: List[Generation], *, partial: bool = False
    ) -> Union[List[AgentAction], AgentFinish]:
        if not isinstance(result[0], ChatGeneration):
            raise ValueError("This output parser only works on ChatGeneration output")
        message = result[0].message
        return parse_ai_message_to_hyperclova_action(message)

    def parse(self, text: str) -> Union[List[AgentAction], AgentFinish]:
        raise ValueError("Can only parse messages")
