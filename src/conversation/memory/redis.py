# -*- coding: UTF-8 -*-
from config import Configuration
from conversation.memory.base import ChatRepository
from conversation.models import ChatTurn


class RedisChatRepository(ChatRepository):

    def __init__(self, config: Configuration):
        super().__init__(config)

    def add_turn(self, conversation_id: str, chat_turn: ChatTurn):
        pass

    def close(self):
        pass
