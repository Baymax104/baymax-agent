# -*- coding: UTF-8 -*-

import ormsgpack
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from redis.asyncio import Redis

from chat.models import ChatTurn, Conversation
from chat.repository import InMemoryChatRepository, MongoDBChatRepository
from monitor import get_logger


logger = get_logger()


class ChatMemory:

    def __init__(self, conversation: Conversation, redis: Redis):
        self.conversation = conversation
        self.redis = redis
        self.window_size = 5
        if conversation.type == "archive":
            self.repo = MongoDBChatRepository()
        elif conversation.type == "temporary":
            self.repo = InMemoryChatRepository()
        else:
            raise NotImplementedError(f"{conversation.type} is not supported")

    async def add(self, chat_turn: ChatTurn):
        updated_content = await self.repo.add(self.conversation.id, chat_turn)
        # update the cache if current conversation type is archive
        if self.conversation.type == "archive":
            cache_key = f"agent:conversation:{self.conversation.id}"
            updated_conversation = self.conversation.model_copy(update={"content": updated_content})
            encoded = ormsgpack.packb(updated_conversation.model_dump())
            await self.redis.set(cache_key, encoded)
            logger.debug(f"Added archive conversation {self.conversation.id}")
        else:
            self.conversation.content = updated_content
            logger.debug(f"Added temporary conversation {self.conversation.id}")

    async def get_message_context(self) -> list[BaseMessage]:
        if self.conversation.type == "archive":
            conversation = await self.redis.get(f"agent:conversation:{self.conversation.id}")
            conversation = ormsgpack.unpackb(conversation)
            content = Conversation.model_validate(conversation).content
        else:
            content = self.conversation.content

        message_window = content[-self.window_size:] if len(content) > self.window_size else content
        logger.debug(f"Message window: {message_window}")
        context = []
        for turn in message_window:
            human_message = HumanMessage(turn.human_message.content)
            ai_message = AIMessage(turn.ai_message.content)
            context.extend([human_message, ai_message])
        return context

