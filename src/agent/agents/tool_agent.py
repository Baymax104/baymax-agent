# -*- coding: UTF-8 -*-
import re

from icecream import ic
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.constants import END, START

from agent.agents.base import GraphAgent
from agent.prompts.tool_agent import *
from workflow import *


class ToolAgent(GraphAgent):
    state_schema = ToolState

    decision_prompt = ChatPromptTemplate.from_messages([
        DECISION_SYSTEM_TEMPLATE,
        MessagesPlaceholder("user")
    ])

    function_call_prompt = ChatPromptTemplate.from_messages([
        FUNCTION_CALL_SYSTEM_TEMPLATE,
        MessagesPlaceholder("user")
    ])

    conclusion_prompt = ChatPromptTemplate.from_messages([
        CONCLUSION_SYSTEM_TEMPLATE,
        MessagesPlaceholder("user")
    ])

    async def chat(self, user_prompt: str):
        if self.workflow is None:
            raise RuntimeError(f"Client not initialized")
        user_message = HumanMessage(user_prompt)
        server_infos = [
            {"name": instance.name, "description": instance.description}
            for instance in self.config.server.instances
        ]

        init_messages = self.decision_prompt.format_prompt(servers=server_infos, user=[user_message]).to_messages()
        init_state = State(messages=init_messages)

        async for event in self.workflow.astream(init_state, stream_mode="values"):
            # if message.content and isinstance(message, AIMessage):
            #     print(message.content, end="")
            ic(event)

    def _get_workflow(self) -> GraphConfig:
        decision_marker = ChatNode(name="decision_maker", llm=self.llm, output_type=ToolState)

        def decision_map(state: ToolState) -> ToolState:
            if not isinstance(state.messages[-1], AIMessage):
                return state
            message = state.messages[-1].content
            if match := re.search(r"server://([^/]+)", message):
                server = match.group(1)
                if server != "null":
                    state.server = server
            return state

        decision_map_node = MapNode(
            name="decision_map",
            input_type=ToolState,
            output_type=ToolState,
            transform=decision_map
        )

        def decision_router(state: ToolState) -> str:
            if state.server is not None and state.server != "null":
                return "function_call_map"
            return "conclusion_map"

        decision_router_node = RouteNode(
            name="decision_router",
            input_type=ToolState,
            router=decision_router
        )

        def conclusion_map(state: ToolState) -> ToolState:
            messages = self.conclusion_prompt.format_prompt(user=[state.messages[1]]).to_messages()
            return ToolState(messages=messages)

        conclusion_map_node = MapNode(
            name="conclusion_map",
            input_type=ToolState,
            output_type=ToolState,
            transform=conclusion_map
        )

        async def function_call_map(state: ToolState) -> ToolState:
            async with self.mcp_client:
                tools = await self.mcp_client.list_tools()
            tool_infos = [
                {"name": tool.name, "description": tool.description}
                for tool in tools
            ]
            messages = self.function_call_prompt.format_prompt(tools=tool_infos, user=[state.messages[1]]).to_messages()
            return ToolState(messages=messages, server=state.server)

        function_call_map_node = MapNode(
            name="function_call_map",
            input_type=ToolState,
            output_type=ToolState,
            transform=function_call_map
        )

        function_caller = FunctionCallNode(
            name="function_caller",
            llm=self.llm,
            client=self.mcp_client
        )

        tool_executor = ToolExecuteNode(
            name="tool_executor",
            client=self.mcp_client
        )

        conclusion = ChatNode(name="conclusion", llm=self.llm)

        graph_config = GraphConfig(
            nodes=[
                decision_marker,
                decision_map_node,
                decision_router_node,
                conclusion_map_node,
                function_call_map_node,
                function_caller,
                tool_executor,
                conclusion
            ],
            edges=[
                (START, "decision_maker"),
                ("decision_maker", "decision_map"),
                ("decision_map", "decision_router"),
                ("conclusion_map", "conclusion"),
                ("function_call_map", "function_caller"),
                ("function_caller", "tool_executor"),
                ("tool_executor", "conclusion"),
                ("conclusion", END)
            ]
        )

        return graph_config
