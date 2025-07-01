# -*- coding: UTF-8 -*-
import asyncio

from icecream import ic

from chat import ChatTurn, Conversation, Message, MongoDBChatRepository
from config import ConfigManager
from conversation.repository import ConversationRepository


def test_conversation():
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
        await repo.add(conversation)
        conversation = await repo.get(conversation.id)
        assert conversation.title == "hello"
        await repo.delete(conversation.id)
        await repo.close()

    asyncio.run(main())


def test_chat_mongodb():
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
        await repo.add(conversation)

        chat_repo = MongoDBChatRepository(config)
        await chat_repo.initialize()

        chat_turn = ChatTurn(
            human_message=Message(role="human", content="Hello human"),
            ai_message=Message(role="ai", content="Hello ai"),
        )
        await chat_repo.add(conversation.id, chat_turn)

        t_conversation = await repo.get(conversation.id)
        ic(t_conversation)

        await chat_repo.close()
        await repo.close()

    asyncio.run(main())
