# -*- coding: UTF-8 -*-
from langchain_core.messages import HumanMessage
from pytest import mark

from agent import Session, ToolAgent
from config import ConfigManager
from conversation.controller import ConversationController
from users import User


queries = ["你好", "123*123等于多少"]


@mark.asyncio
@mark.parametrize("query", queries)
async def test_chat(query: str):
    agent = ToolAgent(ConfigManager.get_config())
    await agent.initialize()
    session = Session(
        user_instructions=["你是一个小学数学教师，你要用温柔的语气与用户交流"],
        context=[HumanMessage(query)]
    )
    state = await agent.chat(session)
    async for chunk in state.stream:
        print(chunk.content, end="")
    await agent.close()


@mark.asyncio
async def test_chat_archive():
    config = ConfigManager.get_config()
    user = User(name="John", instructions=[])
    async with ConversationController(user, config) as controller:
        conversation_id = await controller.create(conversation_type="archive")
        chat_controller = await controller.start_conversation(conversation_id)
        async with chat_controller:
            response = chat_controller.chat("你好")
            async for message in response:
                print(message, end="")
            print()


@mark.asyncio
async def test_chat_temporary():
    config = ConfigManager.get_config()
    user = User(name="John", instructions=[])
    async with ConversationController(user, config) as controller:
        conversation_id = await controller.create(conversation_type="temporary")
        chat_controller = await controller.start_conversation(conversation_id)
        async with chat_controller:
            response = chat_controller.chat("你好")
            async for message in response:
                print(message, end="")
            print()
