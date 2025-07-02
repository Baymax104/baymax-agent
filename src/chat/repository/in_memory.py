# -*- coding: UTF-8 -*-
from chat.models import ChatTurn
from chat.repository.base import ChatRepository
from config import Configuration


class InMemoryChatRepository(ChatRepository):

    def __init__(self, config: Configuration):
        super().__init__(config)
        self.chat_turns = []

    async def initialize(self):
        pass

    async def add(self, conversation_id: str, chat_turn: ChatTurn) -> list[ChatTurn]:
        self.chat_turns.append(chat_turn)
        return self.chat_turns

    async def close(self):
        self.chat_turns.clear()
