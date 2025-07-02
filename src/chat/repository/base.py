# -*- coding: UTF-8 -*-
from abc import ABC, abstractmethod

from chat.models import ChatTurn
from config import Configuration
from utils import AsyncResource


class ChatRepository(AsyncResource, ABC):

    def __init__(self, config: Configuration):
        self.config = config.database

    @abstractmethod
    async def add(self, conversation_id: str, chat_turn: ChatTurn) -> list[ChatTurn]:
        ...
