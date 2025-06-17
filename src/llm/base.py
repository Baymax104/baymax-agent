# -*- coding: UTF-8 -*-
from abc import ABC, abstractmethod
from typing import AsyncIterator, Iterator, Self

from langchain_core.messages import AnyMessage
from mcp import Tool

from config import ModelConfig


class LLMProvider(ABC):

    def __init__(self, config: ModelConfig):
        self.config = config
        # validate config
        if not self.config.api_key:
            raise ValueError("Missing API key")
        if not self.config.model:
            raise ValueError("Missing model")
        self.llm = None

    def bind_tools(self, tools: list) -> Self:
        """bind tools for a llm instance"""
        self.llm = self.llm.bind_tools(tools)
        return self

    @abstractmethod
    def generate(
        self,
        messages: list[AnyMessage],
        *,
        tools: list[Tool] | None = None,
        stream: bool = False
    ) -> AnyMessage | Iterator[AnyMessage]:
        """generate an AI message. if tools are provided, llm will use these tools in this generation."""
        ...

    @abstractmethod
    async def generate_async(
        self,
        messages: list[AnyMessage],
        *,
        tools: list[Tool] | None = None,
        stream: bool = False
    ) -> AnyMessage | AsyncIterator[AnyMessage]:
        """generate an AI message. if tools are provided, llm will use these tools in this generation."""
        ...
