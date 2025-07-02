# -*- coding: UTF-8 -*-

import ormsgpack
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from redis.asyncio import Redis

from chat.models import ChatTurn, Conversation
from chat.repository import InMemoryChatRepository, MongoDBChatRepository
from config import Configuration, RedisConfig
from utils import AsyncResource


class ChatMemory(AsyncResource):

    def __init__(self, conversation: Conversation, config: Configuration):
        self.conversation = conversation
        if conversation.type == "archive":
            self.repo = MongoDBChatRepository(config)
        elif conversation.type == "temporary":
            self.repo = InMemoryChatRepository(config)
        else:
            raise NotImplementedError(f"{conversation.type} is not supported")
        self.redis = self.__init_redis(config.database.redis)
        self.window_size = 5

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
        updated_content = await self.repo.add(self.conversation.id, chat_turn)
        # update the cache if current conversation type is archive
        if self.conversation.type == "archive":
            cache_key = f"agent:conversation:{self.conversation.id}"
            updated_conversation = self.conversation.model_copy(update={"content": updated_content})
            encoded = ormsgpack.packb(updated_conversation.model_dump())
            await self.redis.set(cache_key, encoded)
        else:
            self.conversation.content = updated_content

    async def get_message_context(self) -> list[BaseMessage]:
        if self.conversation.type == "archive":
            conversation = await self.redis.get(f"agent:conversation:{self.conversation.id}")
            conversation = ormsgpack.unpackb(conversation)
            content = Conversation.model_validate(conversation).content
        else:
            content = self.conversation.content

        message_window = content[-self.window_size:] if len(content) > self.window_size else content
        context = []
        for turn in message_window:
            human_message = HumanMessage(turn.human_message.content)
            ai_message = AIMessage(turn.ai_message.content)
            context.extend([human_message, ai_message])
        return context

    async def close(self):
        await self.repo.close()
        await self.redis.aclose()
