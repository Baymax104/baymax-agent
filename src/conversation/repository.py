# -*- coding: UTF-8 -*-

import ormsgpack
from beanie import init_beanie

from chat import Conversation, ConversationDB
from config import Configuration
from monitor import DatabaseError
from utils import AsyncResource, init_mongodb, init_redis


class ConversationRepository(AsyncResource):

    def __init__(self, config: Configuration):
        self.config = config.database.mongodb
        self.mongodb = init_mongodb(config.database.mongodb)
        self.redis = init_redis(config.database.redis)

    async def initialize(self):
        await init_beanie(database=self.mongodb[self.config.db], document_models=[ConversationDB])
        await self.redis.initialize()

    async def add(self, conversation: Conversation):
        conversation = conversation.to_entity()
        await ConversationDB.insert_one(conversation)

    async def get(self, conversation_id: str) -> Conversation | None:
        # get from redis
        cache_key = f"agent:conversation:{conversation_id}"
        if await self.redis.exists(cache_key):
            conversation = await self.redis.get(cache_key)
            conversation = ormsgpack.unpackb(conversation)
            conversation = Conversation.model_validate(conversation)
            return conversation

        # get from mongodb
        conversation = await ConversationDB.get(conversation_id)
        if not conversation:
            return None

        encoded = ormsgpack.packb(conversation.model_dump())
        await self.redis.set(cache_key, encoded)
        return conversation.to_domain()

    async def delete(self, conversation_id: str):
        conversation = await ConversationDB.get(conversation_id)
        if conversation is None:
            raise DatabaseError(f"Conversation {conversation_id} does not exist.")
        await conversation.delete()  # noqa
        await self.redis.delete(f"agent:conversation:{conversation_id}")

    async def close(self):
        self.mongodb.close()
        await self.redis.aclose()
