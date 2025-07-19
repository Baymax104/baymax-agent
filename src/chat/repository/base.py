# -*- coding: UTF-8 -*-
from abc import ABC, abstractmethod

from chat.models import ChatTurn


class ChatRepository(ABC):

    @abstractmethod
    async def add(self, conversation_id: str, chat_turn: ChatTurn) -> list[ChatTurn]:
        ...
