# -*- coding: UTF-8 -*-
from abc import ABC

from fastmcp import Client as MCPClient

from config import Configuration
from llm import LLMProvider


class BaseAgent(ABC):

    def __init__(self, mcp_client: MCPClient, llm: LLMProvider, config: Configuration):
        self.config = config
        self.servers = config.server.instances
        self.mcp_client = mcp_client
        self.llm = llm
