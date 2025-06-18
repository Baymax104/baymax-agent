# -*- coding: UTF-8 -*-
from abc import ABC, abstractmethod
from contextlib import AsyncExitStack

from fastmcp import Client as MCPClient
from fastmcp.client.transports import MCPConfigTransport
from icecream import ic
from langchain_core.messages import HumanMessage
from langgraph.pregel import Pregel
from pydantic import BaseModel

from config import Configuration
from llm import LLMFactory
from workflow import GraphBuilder, GraphConfig


class BaseAgent(ABC):

    # noinspection PyAbstractClass
    def __init__(self, config: Configuration):
        self.config = config
        self.servers = config.server.instances
        self.context = AsyncExitStack()
        self.mcp_client = MCPClient(MCPConfigTransport(config.server.to_mcp()), timeout=10)
        self.llm = LLMFactory.create(config.model)

    async def initialize(self):
        await self.__ping_mcp_server()
        await self.__ping_llm()

    async def __ping_mcp_server(self):
        self.mcp_client = await self.context.enter_async_context(self.mcp_client)
        if not await self.mcp_client.ping():
            raise RuntimeError(f"MCP server connection failed")
        ic("ping mcp successfully")

    async def __ping_llm(self):
        response = await self.llm.generate_async([HumanMessage("Hello")])
        if not response.content:
            raise RuntimeError(f"LLM connection failed")
        ic("ping llm successfully")

    async def close(self):
        try:
            await self.context.aclose()
            ic("close agent successfully")
        except Exception as e:
            ic(e)


class GraphAgent(BaseAgent):
    state_schema: type[BaseModel]
    input_schema: type[BaseModel] | None = None
    output_schema: type[BaseModel] | None = None

    def __init__(self, config: Configuration):
        super().__init__(config)
        self.workflow: Pregel | None = None

    async def initialize(self):
        await super().initialize()
        if self.workflow is not None:
            raise RuntimeError(f"Client already initialized")
        # build graph
        builder = GraphBuilder(self.state_schema, self.input_schema, self.output_schema)
        graph_config = self._get_workflow()
        builder.from_config(graph_config)
        self.workflow = builder.compile()

    @abstractmethod
    def _get_workflow(self) -> GraphConfig:
        ...
