# -*- coding: UTF-8 -*-
from abc import ABC, abstractmethod
from typing import Self

from langchain_core.messages import BaseMessage

from config import ModelConfig


class LLMProvider(ABC):

    def __init__(self, config: ModelConfig):
        self.config = config
        # validate config
        if self.config.api_key is None:
            raise ValueError("Missing API key")
        if self.config.model is None:
            raise ValueError("Missing model")

    @abstractmethod
    def with_tools(self, tools: list) -> Self:
        ...

    @abstractmethod
    def generate(self, messages: list[BaseMessage]) -> BaseMessage:
        ...
