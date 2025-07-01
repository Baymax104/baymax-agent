# -*- coding: UTF-8 -*-
from agent import Session
from chat import ChatTurn, Conversation, InMemoryChatRepository, MongoDBChatRepository
from config import Configuration


class ChatMemory:

    def __init__(self, conversation: Conversation, config: Configuration):
        self.conversation = conversation
        if conversation.type == "archive":
            self.repo = MongoDBChatRepository(config)
        elif conversation.type == "temporary":
            self.repo = InMemoryChatRepository(config)
        else:
            raise NotImplementedError(f"{conversation.type} is not supported")

    async def initialize(self):
        await self.repo.initialize()

    async def add(self, chat_turn: ChatTurn):
        await self.repo.add(self.conversation.id, chat_turn)

    def get_session(self) -> Session:
        ...

    async def close(self):
        await self.repo.close()
