# -*- coding: UTF-8 -*-
from typing import Self

from redis.asyncio import Redis

from agent import Session
from chat.models import ChatTurn, Conversation
from chat.repository import InMemoryChatRepository, MongoDBChatRepository
from config import Configuration, RedisConfig


class ChatMemory:

    def __init__(self, conversation: Conversation, config: Configuration):
        self.conversation = conversation
        if conversation.type == "archive":
            self.repo = MongoDBChatRepository(config)
        elif conversation.type == "temporary":
            self.repo = InMemoryChatRepository(config)
        else:
            raise NotImplementedError(f"{conversation.type} is not supported")
        self.redis = self.__init_redis(config.database.redis)

    def __init_redis(self, config: RedisConfig):
        if not config.host or not config.port:
            raise ConnectionError("Host and port are required.")
        db = config.db if config.db else 0
        redis = Redis(
            host=config.host,
            port=config.port,
            password=config.password,
            db=db,
        )
        return redis

    async def initialize(self):
        await self.repo.initialize()
        await self.redis.initialize()

    async def add(self, chat_turn: ChatTurn):
        await self.repo.add(self.conversation.id, chat_turn)
        # inactivate the cache
        cache_key = f"agent:conversation:{self.conversation.id}"
        if await self.redis.exists(cache_key):
            await self.redis.delete(cache_key)

    def get_session(self) -> Session:
        ...

    async def close(self):
        await self.repo.close()
        await self.redis.aclose()

    async def __aenter__(self) -> Self:
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
