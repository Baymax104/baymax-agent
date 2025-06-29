# -*- coding: UTF-8 -*-
import asyncio

import ormsgpack
from icecream import ic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from config import ConfigManager
from conversation import Conversation, Session
from conversation.repository import ConversationRepository


def test_messagepack():
    session = Session(
        context=[
            SystemMessage("Hello"),
            HumanMessage("你好"),
            AIMessage("hello", tool_calls=[{"name": "hello", "args": {}, "id": "abc"}]),
            ToolMessage("你好", tool_call_id="abc")
        ]
    )
    ic(session)
    session = ormsgpack.packb(session.model_dump())
    ic(type(session), session)

    session = ormsgpack.unpackb(session)
    session = Session.model_validate(session)
    ic(session)


def test_mongodb():
    async def main():
        config = ConfigManager.get_config()
        repo = ConversationRepository(config)
        await repo.initialize()

        conversation = Conversation(
            user_id="bcd",
            title="hello",
            type="archive",
        )
        ic(conversation)
        await repo.add_conversation(conversation)
        conversation = await repo.get_conversation(conversation.id)
        assert conversation.title == "hello"
        await repo.delete_conversation(conversation.id)
        repo.close()

    asyncio.run(main())
