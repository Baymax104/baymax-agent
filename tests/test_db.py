# -*- coding: UTF-8 -*-

import ormsgpack
from icecream import ic
from pytest import mark

from chat.models import ChatTurn, Conversation, Message
from injection import Container


container = Container()


@mark.asyncio
async def test_conversation():
    await container.init_resources()
    repo = await container.chat.conversation_repository()

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
    await container.shutdown_resources()


@mark.asyncio
async def test_redis():
    await container.init_resources()
    redis = await container.database.redis()
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
    await container.shutdown_resources()


@mark.asyncio
async def test_chat_memory_in_db():
    await container.init_resources()
    repo = await container.chat.conversation_repository()
    conversation = Conversation(
        user_id="bcd",
        title="hello",
        type="archive",
    )
    await repo.add(conversation)
    # activate cache
    conversation = await repo.get(conversation.id)
    assert await repo.redis.exists(f"agent:conversation:{conversation.id}")
    container.current.conversation.override(conversation)
    memory = await container.chat.chat_memory()
    chat_turn = ChatTurn(
        human_message=Message(role="human", content="Hello human1"),
        ai_message=Message(role="ai", content="Hello ai1"),
    )
    # update cache
    await memory.add(chat_turn)
    assert await repo.redis.exists(f"agent:conversation:{conversation.id}")

    # activate cache
    conversation = await repo.get(conversation.id)
    assert await repo.redis.exists(f"agent:conversation:{conversation.id}")
    ic(conversation)

    await repo.delete(conversation.id)
    await container.shutdown_resources()


@mark.asyncio
async def test_chat_memory_in_memory():
    await container.init_resources()
    repo = await container.chat.conversation_repository()
    conversation = Conversation(
        user_id="bcd",
        title="hello",
        type="temporary",
    )
    await repo.add(conversation)
    # activate cache
    conversation = await repo.get(conversation.id)
    assert await repo.redis.exists(f"agent:conversation:{conversation.id}")
    container.current.conversation.override(conversation)
    memory = await container.chat.chat_memory()
    chat_turn = ChatTurn(
        human_message=Message(role="human", content="Hello human1"),
        ai_message=Message(role="ai", content="Hello ai1"),
    )
    # update cache
    await memory.add(chat_turn)
    assert await repo.redis.exists(f"agent:conversation:{conversation.id}")

    # activate cache
    conversation = await repo.get(conversation.id)
    assert await repo.redis.exists(f"agent:conversation:{conversation.id}")
    ic(conversation)

    await repo.delete(conversation.id)
    await container.shutdown_resources()
