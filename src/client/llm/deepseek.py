# -*- coding: UTF-8 -*-
from langchain_core.messages import BaseMessage
from langchain_deepseek import ChatDeepSeek

from client.llm.base import LLMProvider
from config import ModelConfig


class DeepSeek(LLMProvider):

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.llm = ChatDeepSeek(
            model=config.model,
            api_key=config.api_key,
            **config.generation
        )

    def generate(self, messages: list[BaseMessage], *, tools: list | None = None):
        llm = self.llm.bind_tools(tools) if tools else self.llm
        ai_message = llm.invoke(messages)
        messages.append(ai_message)
        return messages
