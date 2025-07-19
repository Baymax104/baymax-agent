# -*- coding: UTF-8 -*-
from chat.models import ChatTurn
from chat.repository.base import ChatRepository


class InMemoryChatRepository(ChatRepository):

    def __init__(self):
        super().__init__()
        self.chat_turns = []

    async def add(self, conversation_id: str, chat_turn: ChatTurn) -> list[ChatTurn]:
        self.chat_turns.append(chat_turn)
        return self.chat_turns
