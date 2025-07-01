# -*- coding: UTF-8 -*-
import re

from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.graph import add_messages
from mcp.types import TextContent

from agent.agents.base import BaseAgent
from agent.models import ChatState, Session
from agent.prompts.tool_agent import *
from monitor import AgentError, MCPToolError, get_logger


logger = get_logger()


class ToolAgent(BaseAgent):

    @logger.catch_exception()
    async def chat(self, session: Session) -> ChatState:
        if not session.context:
            raise AgentError("Session context is empty")
        if not isinstance(session.context[-1], HumanMessage):
            raise AgentError("Last session context is not of type HumanMessage")
        user_message = session.context[-1]
        middle_messages = []

        # generate decision
        decision_messages = decision_prompt(servers=self.servers, history=[user_message])
        decision = await self.llm.generate_async(decision_messages)

        # extract server
        server = re.search(r"server://([^/]+)", decision.content)
        if not server or server.group(1) == "null":
            logger.info("No server selected")
            return await self.__common_chat(session)
        server = server.group(1)

        # get server tools
        tools = await self.mcp_client.list_tools()
        server_tools = [tool for tool in tools if tool.name.startswith(server)]
        if not server_tools:
            server_tools = tools

        logger.info(f"Server \"{server}\" selected, available tools: [{', '.join(tool.name for tool in server_tools)}]")

        # function call
        function_call_messages = function_call_prompt(tools=server_tools, history=[user_message])
        function_call = await self.llm.generate_async(function_call_messages, tools=server_tools)
        if not function_call.tool_calls:
            logger.debug("No function call in message")
            return await self.__common_chat(session)
        middle_messages = add_messages(middle_messages, function_call)

        # tool execute
        tool_call = function_call.tool_calls[0]
        logger.debug(f"Tool call: {tool_call}")
        result = await self.mcp_client.call_tool(tool_call["name"], tool_call["args"])
        result = result[0]
        if not isinstance(result, TextContent):
            raise MCPToolError(f"Tool call {tool_call['name']} returned {type(result)}")
        logger.debug(f"Tool execution result: {result}")
        tool_message = ToolMessage(result.text, tool_call_id=tool_call["id"])
        middle_messages = add_messages(middle_messages, tool_message)

        # add session history
        conclusion_messages = conclusion_prompt(
            instructions=session.user_instructions,
            history=[*session.context, function_call, tool_message],
        )

        # conclude and return answer stream
        stream = await self.llm.generate_async(conclusion_messages, stream=True)
        return ChatState(middle=middle_messages, stream=stream)

    async def __common_chat(self, session: Session) -> ChatState:
        """common chat for error fallback"""
        messages = common_prompt(instructions=session.user_instructions, history=session.context)
        stream = await self.llm.generate_async(messages, stream=True)
        return ChatState(stream=stream)
