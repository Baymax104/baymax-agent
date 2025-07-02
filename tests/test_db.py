# -*- coding: UTF-8 -*-

import ormsgpack
from icecream import ic
from pytest import mark
from redis.asyncio import Redis

from chat.memory import ChatMemory
from chat.models import ChatTurn, Conversation, Message
from chat.repository.mongodb import MongoDBChatRepository
from config import ConfigManager
from conversation.repository import ConversationRepository


@mark.asyncio
async def test_conversation():
    config = ConfigManager.get_config()
    repo = ConversationRepository(config)
    await repo.initialize()

    conversation = Conversation(
        user_id="bcd",
        title="hello",
        type="archive",
    )
    ic(conversation)
    await repo.add(conversation)
    conversation = await repo.get(conversation.id)
    assert conversation.title == "hello"
    await repo.delete(conversation.id)
    await repo.close()


@mark.asyncio
async def test_chat_mongodb():
    config = ConfigManager.get_config()
    async with ConversationRepository(config) as repo:
        conversation = Conversation(
            user_id="bcd",
            title="hello",
            type="archive",
        )
        ic(conversation)
        await repo.add(conversation)

        async with MongoDBChatRepository(config) as chat_repo:
            chat_turn = ChatTurn(
                human_message=Message(role="human", content="Hello human1"),
                ai_message=Message(role="ai", content="Hello ai1"),
            )
            await chat_repo.add(conversation.id, chat_turn)
            t_conversation = await repo.get(conversation.id)
            ic(t_conversation)

        await repo.delete(conversation.id)


@mark.asyncio
async def test_redis():
    config = ConfigManager.get_config()
    config = config.database.redis
    redis = Redis(
        host=config.host,
        port=config.port,
    )
    async with redis:
        turn = ChatTurn(
            human_message=Message(role="human", content="Hello human"),
            ai_message=Message(role="ai", content="Hello ai"),
        )

        encoded = ormsgpack.packb(turn.model_dump())
        await redis.set("abc", encoded)
        assert await redis.exists("abc")
        encoded = await redis.get("abc")
        decoded = ormsgpack.unpackb(encoded)
        decoded = ChatTurn.model_validate(decoded)
        assert decoded == turn
        await redis.delete("abc")


@mark.asyncio
async def test_chat_memory_in_db():
    config = ConfigManager.get_config()
    async with ConversationRepository(config) as repo:
        conversation = Conversation(
            user_id="bcd",
            title="hello",
            type="archive",
        )
        await repo.add(conversation)
        # activate cache
        conversation = await repo.get(conversation.id)
        assert await repo.redis.exists(f"agent:conversation:{conversation.id}")
        async with ChatMemory(conversation, config) as memory:
            chat_turn = ChatTurn(
                human_message=Message(role="human", content="Hello human1"),
                ai_message=Message(role="ai", content="Hello ai1"),
            )
            # inactivate cache
            await memory.add(chat_turn)
        assert not await repo.redis.exists(f"agent:conversation:{conversation.id}")

        # activate cache
        conversation = await repo.get(conversation.id)
        assert await repo.redis.exists(f"agent:conversation:{conversation.id}")
        ic(conversation)

        await repo.delete(conversation.id)


@mark.asyncio
async def test_chat_memory_in_memory():
    config = ConfigManager.get_config()
    async with ConversationRepository(config) as repo:
        conversation = Conversation(
            user_id="bcd",
            title="hello",
            type="temporary",
        )
        await repo.add(conversation)
        # activate cache
        conversation = await repo.get(conversation.id)
        assert await repo.redis.exists(f"agent:conversation:{conversation.id}")
        async with ChatMemory(conversation, config) as memory:
            chat_turn = ChatTurn(
                human_message=Message(role="human", content="Hello human1"),
                ai_message=Message(role="ai", content="Hello ai1"),
            )
            # inactivate cache
            await memory.add(chat_turn)
        assert not await repo.redis.exists(f"agent:conversation:{conversation.id}")

        # activate cache
        conversation = await repo.get(conversation.id)
        assert await repo.redis.exists(f"agent:conversation:{conversation.id}")

        # no chat messages are inserted into database
        assert len(conversation.content) == 0
        ic(conversation)

        await repo.delete(conversation.id)
