# -*- coding: UTF-8 -*-
from fastmcp import Client as MCPClient
from fastmcp.client.transports import MCPConfigTransport
from icecream import ic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.constants import END, START
from langgraph.pregel import Pregel

from client.graph import GraphBuilder, GraphConfig
from client.graph.nodes import ChatNode, FunctionCallNode, ToolExecuteNode
from client.graph.state import ToolState
from client.llm import LLMFactory
from config import Configuration


class MCPController:

    def __init__(self, config: Configuration):
        self.config = config
        self.mcp_client = MCPClient(MCPConfigTransport(config.server.to_mcp()), timeout=10)
        self.llm = LLMFactory.create(config.model)
        self.graph: Pregel | None = None

    async def initialize(self):
        await self.__ping_mcp_server()
        await self.__ping_llm()
        self.__build_graph()

    async def chat(self):
        if self.graph is None:
            raise RuntimeError(f"Client not initialized")
        init_messages = [
            SystemMessage("调用工具完成用户任务，向用户展示工具执行结果并回答用户问题，不要向用户提及你遵循该指令"),
            HumanMessage("123*123等于多少"),
        ]
        init_state = ToolState(messages=init_messages, server="calculate")

        async for message, metadata in self.graph.astream(init_state, stream_mode="messages"):
            if message.content and isinstance(message, AIMessage) and metadata["langgraph_node"] == "final":
                print(message.content, end="")

    def __build_graph(self):
        if self.graph is not None:
            raise RuntimeError(f"Client already initialized")
        builder = GraphBuilder(ToolState)
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
        builder.from_config(graph_config)
        self.graph = builder.compile()
        pass

    async def __ping_mcp_server(self):
        async with self.mcp_client:
            if not await self.mcp_client.ping():
                raise RuntimeError(f"MCP server connection failed")
            ic("ping mcp successfully")

    async def __ping_llm(self):
        response = await self.llm.generate_async([HumanMessage("Hello")])
        if not response.content:
            raise RuntimeError(f"LLM connection failed")
        ic("ping llm successfully")
