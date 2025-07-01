# -*- coding: UTF-8 -*-
from abc import ABC
from contextlib import AsyncExitStack

from fastmcp import Client as MCPClient
from fastmcp.client.transports import MCPConfigTransport
from langchain_core.messages import HumanMessage

from config import Configuration
from llm import LLMFactory
from monitor import LLMConnectionError, MCPConnectionError, get_logger


logger = get_logger()


class BaseAgent(ABC):

    # noinspection PyAbstractClass
    def __init__(self, config: Configuration):
        self.config = config
        self.servers = config.server.instances
        self.context = AsyncExitStack()
        self.mcp_client = MCPClient(MCPConfigTransport(config.server.to_mcp()), timeout=10)
        self.llm = LLMFactory.create(config.model)

    @logger.catch_exception(throw=True)
    async def initialize(self):
        await self.__ping_mcp_server()
        await self.__ping_llm()

    async def __ping_mcp_server(self):
        self.mcp_client = await self.context.enter_async_context(self.mcp_client)
        if not await self.mcp_client.ping():
            raise MCPConnectionError(f"MCP server connection failed")
        logger.success("MCP server connection established")

    async def __ping_llm(self):
        response = await self.llm.generate_async([HumanMessage("Hello")])
        if not response.content:
            raise LLMConnectionError(f"LLM connection failed")
        logger.success("LLM connection established")

    @logger.catch_exception(throw=True)
    async def close(self):
        await self.context.aclose()
        logger.success(f"Agent closed successfully")
