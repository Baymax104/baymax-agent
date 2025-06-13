# -*- coding: UTF-8 -*-
from typing import Self

from langchain_core.messages import BaseMessage
from langchain_deepseek import ChatDeepSeek

from client.llm.base import LLMProvider
from config import ModelConfig


class DeepSeek(LLMProvider):

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        generation = config.generation if config.generation else {}
        self.llm = ChatDeepSeek(
            model=config.model,
            api_key=config.api_key,
            **generation
        )

    def with_tools(self, tools: list) -> Self:
        self.llm.bind_tools(tools)
        return self

    def generate(self, messages: list[BaseMessage]) -> BaseMessage:
        return self.llm.invoke(messages)
