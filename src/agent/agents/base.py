# -*- coding: UTF-8 -*-
from abc import ABC
from contextlib import AsyncExitStack

from fastmcp import Client as MCPClient
from fastmcp.client.transports import MCPConfigTransport
from icecream import ic
from langchain_core.messages import HumanMessage

from config import Configuration
from llm import LLMFactory


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

