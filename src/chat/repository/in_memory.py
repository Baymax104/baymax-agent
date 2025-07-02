# -*- coding: UTF-8 -*-
from chat.models import ChatTurn
from chat.repository.base import ChatRepository
from config import Configuration


class InMemoryChatRepository(ChatRepository):

    def __init__(self, config: Configuration):
        super().__init__(config)
        self.messages = []


    async def initialize(self):
        pass

    async def add(self, conversation_id: str, chat_turn: ChatTurn):
        self.messages.append(chat_turn)

    async def close(self):
        self.messages.clear()
