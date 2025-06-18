# -*- coding: UTF-8 -*-
import re
from typing import AsyncIterator

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import add_messages
from mcp.types import TextContent

from agent.agents.base import BaseAgent
from agent.prompts.tool_agent import *
from monitor import MCPToolError, logger
from workflow import *


class ToolAgent(BaseAgent):

    decision_prompt = ChatPromptTemplate.from_messages([
        DECISION_SYSTEM_TEMPLATE,
        MessagesPlaceholder("user")
    ])

    function_call_prompt = ChatPromptTemplate.from_messages([
        FUNCTION_CALL_SYSTEM_TEMPLATE,
        MessagesPlaceholder("user")
    ])

    common_template = ChatPromptTemplate.from_messages([
        COMMON_SYSTEM_TEMPLATE,
        MessagesPlaceholder("user")
    ])

    @logger.catch_exception()
    async def chat(self, user_prompt: str) -> AsyncIterator[AnyMessage]:
        user_message = HumanMessage(user_prompt)
        messages = self.decision_prompt.format_messages(servers=self.servers, user=[user_message])

        # decision
        decision_message = await self.llm.generate_async(messages)

        # extract server
        server = re.search(r"server://([^/]+)", decision_message.content)
        if not server or server.group(1) == "null":
            logger.info("No server selected")
            return await self.__common_chat(user_message)
        server = server.group(1)

        # get server tools
        tools = await self.mcp_client.list_tools()
        server_tools = [tool for tool in tools if tool.name.startswith(server)]
        if not server_tools:
            server_tools = tools

        logger.info(f"Server \"{server}\" selected, available tools: [{', '.join(tool.name for tool in server_tools)}]")

        # function call
        messages = self.function_call_prompt.format_messages(tools=server_tools, user=[user_message])
        function_call = await self.llm.generate_async(messages, tools=server_tools)
        if not function_call.tool_calls:
            logger.debug("No function call in message")
            return await self.__common_chat(user_message)
        messages = add_messages(messages, function_call)

        # tool execute
        tool_call = function_call.tool_calls[0]
        logger.debug(f"Tool call: {tool_call}")
        result = await self.mcp_client.call_tool(tool_call["name"], tool_call["args"])
        result = result[0]
        if not isinstance(result, TextContent):
            raise MCPToolError(f"Tool call {tool_call['name']} returned {type(result)}")
        logger.debug(f"Tool execution result: {result}")
        tool_message = ToolMessage(result.text, tool_call_id=tool_call["id"])
        messages = add_messages(messages, tool_message)

        # conclude and return answer stream
        return await self.llm.generate_async(messages, stream=True)

    async def __common_chat(self, user_message: HumanMessage) -> AsyncIterator[AnyMessage]:
        """common chat for error fallback"""
        messages = self.common_template.format_messages(user=[user_message])
        return await self.llm.generate_async(messages, stream=True)
