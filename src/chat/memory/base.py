# -*- coding: UTF-8 -*-
from abc import ABC, abstractmethod

from chat.models import ChatTurn
from config import Configuration


class ChatRepository(ABC):

    def __init__(self, config: Configuration):
        self.config = config.database

    @abstractmethod
    async def initialize(self):
        ...

    @abstractmethod
    async def add(self, conversation_id: str, chat_turn: ChatTurn):
        ...

    @abstractmethod
    async def close(self):
        ...
