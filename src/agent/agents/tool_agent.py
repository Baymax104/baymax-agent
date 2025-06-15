# -*- coding: UTF-8 -*-
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.constants import END, START

from agent.agents.base import Agent
from agent.prompts.tool_agent import *
from workflow import *


class ToolAgent(Agent):
    state_schema = ToolState

    decision_prompt = ChatPromptTemplate.from_messages(
        [
            DECISION_SYSTEM_TEMPLATE,
            MessagesPlaceholder("user")
        ]
    )

    function_call_prompt = ChatPromptTemplate.from_messages(
        [
            FUNCTION_CALL_SYSTEM_TEMPLATE,
            MessagesPlaceholder("user")
        ]
    )

    async def chat(self):
        if self.workflow is None:
            raise RuntimeError(f"Client not initialized")
        init_messages = [
            SystemMessage("你必须调用工具完成用户任务，向用户展示工具执行结果并回答用户问题，不要向用户提及你遵循该指令"),
            HumanMessage("123*123等于多少"),
        ]
        init_state = ToolState(messages=init_messages, server="calculate")

        async for message, metadata in self.workflow.astream(init_state, stream_mode="messages"):
            if message.content and isinstance(message, AIMessage) and metadata["langgraph_node"] == "final":
                print(message.content, end="")

    def _get_workflow(self) -> GraphConfig:
        graph_config = GraphConfig(
            nodes=[
                FunctionCallNode(name="function_call", llm=self.llm, client=self.mcp_client),
                ToolExecuteNode(name="tool_call", client=self.mcp_client),
                ChatNode(name="final", llm=self.llm)
            ],
            edges=[
                (START, "function_call"),
                ("function_call", "tool_call"),
                ("tool_call", "final"),
                ("final", END)
            ]
        )

        return graph_config
