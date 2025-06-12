# -*- coding: UTF-8 -*-
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import BaseMessage

from client.llm.base import LLMProvider
from config import ModelConfig


class ZhipuAI(LLMProvider):

    def __init__(self, config: ModelConfig):
        super().__init__(config)
        self.llm = ChatZhipuAI(
            model=config.model,
            api_key=config.api_key,
            **config.generation
        )

    def generate(self, messages: list[BaseMessage], *, tools: list | None = None) -> list[BaseMessage]:
        llm = self.llm.bind_tools(tools) if tools else self.llm
        ai_message = llm.invoke(messages)
        messages.append(ai_message)
        return messages
