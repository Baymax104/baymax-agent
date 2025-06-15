# -*- coding: UTF-8 -*-
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import AnyMessage
from mcp import Tool

from agent.llm.base import LLMProvider
from agent.llm.utils import convert_to_openai_tools
from config import ModelConfig


class ZhipuAI(LLMProvider):

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        generation = config.generation if config.generation else {}
        self.llm = ChatZhipuAI(
            model=config.model,
            api_key=config.api_key,
            **generation
        )

    def generate(self, messages: list[AnyMessage], *, tools: list[Tool] | None = None) -> AnyMessage:
        llm = self.llm.bind_tools(convert_to_openai_tools(tools)) if tools else self.llm
        # Do not replace self.llm with llm
        return llm.invoke(messages)

    async def generate_async(self, messages: list[AnyMessage], *, tools: list[Tool] | None = None) -> AnyMessage:
        llm = self.llm.bind_tools(convert_to_openai_tools(tools)) if tools else self.llm
        # Do not replace self.llm with llm
        return await llm.ainvoke(messages)
