# -*- coding: UTF-8 -*-
from redis.asyncio import Redis

from chat.memory.base import ChatRepository
from chat.models import ChatTurn
from config import Configuration, RedisConfig


class InMemoryChatRepository(ChatRepository):

    def __init__(self, config: Configuration):
        super().__init__(config)
        self.redis = self.__init_redis(config.database.redis)

    def __init_redis(self, config: RedisConfig):
        redis = Redis(
            host=config.host,
            port=config.port,
            password=config.password,
            db=config.db,
        )
        return redis

    async def initialize(self):
        pass

    def add(self, conversation_id: str, chat_turn: ChatTurn):
        pass

    async def close(self):
        pass
