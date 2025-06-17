# -*- coding: UTF-8 -*-
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine

from fastmcp import Client as MCPClient
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.constants import END, START
from langgraph.graph import add_messages
from mcp.types import TextContent
from pydantic import BaseModel, ConfigDict

from llm import LLMProvider
from workflow.state import State, ToolState


class Node[Input, Output](ABC, BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
    name: str
    input_type: type[Input]
    output_type: type[Output]

    @abstractmethod
    def __call__(self, state: Input) -> Output:
        ...


# noinspection PyTypeChecker
class StateNode[Input: State, Output: State](Node[Input, Output], ABC):
    input_type: type[Input] = State
    output_type: type[Output] = State

    @abstractmethod
    async def __call__(self, state: Input) -> Output:
        ...


# noinspection PyTypeChecker
class LLMNode[Input: State, Output: State](StateNode[Input, Output], ABC):
    llm: LLMProvider


# noinspection PyTypeChecker
class ChatNode[Input: State, Output: State](LLMNode[Input, Output]):

    async def __call__(self, state: Input) -> Output:
        messages = await self.llm.generate_async(state.messages)
        messages = add_messages(state.messages, [messages])
        return self.output_type(messages=messages)


# noinspection PyTypeChecker
class FunctionCallNode[Input: ToolState, Output: ToolState](LLMNode[Input, Output]):
    input_type: type[Input] = ToolState
    output_type: type[Output] = ToolState
    client: MCPClient

    async def __call__(self, state: Input) -> Output:
        async with self.client:
            tools = await self.client.list_tools()
        server_tools = [tool for tool in tools if tool.name.startswith(state.server)]
        if not server_tools:
            server_tools = tools  # use all tools if only single server is connected
        ai_message = await self.llm.generate_async(state.messages, tools=server_tools)
        return ToolState(
            messages=add_messages(state.messages, [ai_message]),
            server=state.server,
            tool_calls=ai_message.tool_calls
        )


# noinspection PyTypeChecker
class ToolExecuteNode[Input: ToolState, Output: ToolState](StateNode[Input, Output]):
    input_type: type[Input] = ToolState
    output_type: type[Output] = ToolState
    client: MCPClient

    async def __call__(self, state: Input) -> Output:
        if not isinstance(state.messages[-1], AIMessage):
            raise ValueError(f"Last message is not an AIMessage")
        if not state.server:
            raise ValueError(f"Server is null")
        if not state.tool_calls:
            raise ValueError(f"Tool calls are empty")
        async with self.client:
            tool_call = state.tool_calls[0]  # Usually there is only one tool_call
            results = await self.client.call_tool(tool_call["name"], tool_call["args"])
        result = results[0]
        if not isinstance(result, TextContent):
            raise ValueError(f"{tool_call['name']} returned {type(result)}")
        tool_message = ToolMessage(result.text, tool_call_id=tool_call["id"])
        return ToolState(
            messages=add_messages(state.messages, [tool_message]),
            server=state.server,
            tool_calls=state.tool_calls
        )


# noinspection PyTypeChecker
class MapNode[Input: State, Output: State](StateNode[Input, Output]):
    input_type: type[Input] = State
    output_type: type[Output] = State
    transform: Callable[[Input], Output | Coroutine[Any, Any, Output]]

    async def __call__(self, state: Input) -> Output:
        result = self.transform(state)
        if isinstance(result, Coroutine):
            return await result
        return result


# noinspection PyTypeChecker
class RouteNode[Input: State](Node[Input, str]):
    input_type: type[Input] = State
    output_type: type[str] = str
    router: Callable[[Input], str]

    def __call__(self, state: Input) -> str:
        return self.router(state)


# noinspection PyTypeChecker
class StartNode(Node[Any, None]):
    name: str = START
    input_type: type[Any] = None
    output_type: type[None] = None

    def __call__(self, state: Any):
        return


# noinspection PyTypeChecker
class EndNode(Node[Any, None]):
    name: str = END
    input_type: type[Any] = None
    output_type: type[None] = None

    def __call__(self, state: Any):
        return
