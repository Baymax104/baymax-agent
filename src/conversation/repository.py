# -*- coding: UTF-8 -*-

import ormsgpack
from redis.asyncio import Redis

from chat import Conversation, ConversationDB
from monitor import DatabaseError


class ConversationRepository:

    def __init__(self, redis: Redis):
        self.redis = redis

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

    async def get_all(self) -> list[Conversation]:
        conversations = await ConversationDB.find_all().to_list()
        # flush cache
        for conversation in conversations:
            cache_key = f"agent:conversation:{conversation.id}"
            encoded = ormsgpack.packb(conversation.model_dump())
            await self.redis.set(cache_key, encoded)
        return [conversation.to_domain() for conversation in conversations]

    async def delete(self, conversation_id: str):
        conversation = await ConversationDB.get(conversation_id)
        if conversation is None:
            raise DatabaseError(f"Conversation {conversation_id} does not exist.")
        await conversation.delete()  # noqa
        await self.redis.delete(f"agent:conversation:{conversation_id}")

