# -*- coding: UTF-8 -*-
from abc import ABC, abstractmethod

from config import Configuration
from conversation.models import ChatTurn, Session


class ChatRepository(ABC):

    def __init__(self, config: Configuration):
        self.config = config

    @abstractmethod
    def add_turn(self, conversation_id: str, chat_turn: ChatTurn):
        ...

    @abstractmethod
    def close(self):
        ...


class ChatMemory(ABC):

    def __init__(self, repository: ChatRepository):
        self.repo = repository

    @abstractmethod
    def add(self, conversation_id: str, chat_turn: ChatTurn):
        ...

    @abstractmethod
    def get_session(self, conversation_id: str) -> Session:
        ...

    @abstractmethod
    def close(self):
        ...
