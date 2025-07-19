# -*- coding: UTF-8 -*-
from langchain_core.messages import HumanMessage
from pytest import mark

from agent import Session
from injection import Container


queries = ["123*123等于多少"]
container = Container()


@mark.asyncio
@mark.parametrize("query", queries)
async def test_chat(query: str):
    await container.init_resources()
    agent = await container.agent.tool_agent()
    session = Session(
        user_instructions=["你是一个小学数学教师，你要用温柔的语气与用户交流"],
        context=[HumanMessage(query)]
    )
    state = await agent.chat(session)
    async for chunk in state.stream:
        print(chunk.content, end="")
    await container.shutdown_resources()


@mark.asyncio
async def test_chat_archive():
    await container.init_resources()
    controller = await container.conversation_controller()
    conversation_id = await controller.create(conversation_type="archive")
    conversation = await controller.get(conversation_id)
    container.current.conversation.override(conversation)
    chat_controller = await container.chat_controller()
    response = chat_controller.chat("你好")
    async for message in response:
        print(message, end="")
    print()
    await container.shutdown_resources()


@mark.asyncio
async def test_chat_temporary():
    await container.init_resources()
    controller = await container.conversation_controller()
    conversation_id = await controller.create(conversation_type="archive")
    conversation = await controller.get(conversation_id)
    container.current.conversation.override(conversation)
    chat_controller = await container.chat_controller()
    response = chat_controller.chat("你好")
    async for message in response:
        print(message, end="")
    print()
    await container.shutdown_resources()
