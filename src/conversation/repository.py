# -*- coding: UTF-8 -*-
from typing import Self

import ormsgpack
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis

from chat import Conversation
from config import Configuration, MongoDBConfig, RedisConfig
from monitor import DatabaseError


class ConversationRepository:

    def __init__(self, config: Configuration):
        self.config = config.database.mongodb
        self.mongodb = self.__init_mongodb(config.database.mongodb)
        self.redis = self.__init_redis(config.database.redis)

    def __init_mongodb(self, config: MongoDBConfig):
        if not config.host or not config.port:
            raise ConnectionError("Host and port are required.")
        if not config.db:
            raise ConnectionError("Database is required.")
        user_part = f"{config.user}:{config.password}@" if config.user else ""
        uri = f"mongodb://{user_part}{config.host}:{config.port}"
        client = AsyncIOMotorClient(uri)
        return client

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
        await init_beanie(database=self.mongodb[self.config.db], document_models=[Conversation])
        await self.redis.initialize()

    async def add(self, conversation: Conversation):
        await Conversation.insert_one(conversation)

    async def get(self, conversation_id: str) -> Conversation | None:
        # get from redis
        cache_key = f"agent:conversation:{conversation_id}"
        if await self.redis.exists(cache_key):
            conversation = await self.redis.get(cache_key)
            conversation = ormsgpack.unpackb(conversation)
            conversation = Conversation.model_validate(conversation)
            return conversation

        # get from mongodb
        conversation = await Conversation.get(conversation_id)
        if not conversation:
            return None

        encoded = ormsgpack.packb(conversation.model_dump())
        await self.redis.set(cache_key, encoded)
        return conversation

    async def delete(self, conversation_id: str):
        conversation = await Conversation.get(conversation_id)
        if conversation is None:
            raise DatabaseError(f"Conversation {conversation_id} does not exist.")
        await conversation.delete()  # noqa
        await self.redis.delete(f"agent:conversation:{conversation_id}")

    async def close(self):
        self.mongodb.close()
        await self.redis.aclose()

    async def __aenter__(self) -> Self:
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
