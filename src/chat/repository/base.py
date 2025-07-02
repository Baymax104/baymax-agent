# -*- coding: UTF-8 -*-
from abc import ABC, abstractmethod
from typing import Self

from chat.models import ChatTurn
from config import Configuration


class ChatRepository(ABC):

    def __init__(self, config: Configuration):
        self.config = config.database

    @abstractmethod
    async def initialize(self):
        ...

    @abstractmethod
    async def add(self, conversation_id: str, chat_turn: ChatTurn) -> list[ChatTurn]:
        ...

    @abstractmethod
    async def close(self):
        ...

    async def __aenter__(self) -> Self:
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
