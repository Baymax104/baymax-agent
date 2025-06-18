# -*- coding: UTF-8 -*-
import asyncio

from pytest import mark

from agent import ToolAgent
from config import ConfigManager


queries = ["你好", "123*123等于多少"]


@mark.parametrize("query", queries)
def test_chat(query: str):
    async def main():
        agent = ToolAgent(ConfigManager.get_config())
        await agent.initialize()
        async for chunk in await agent.chat(query):
            print(chunk.content, end="")
        await agent.close()

    asyncio.run(main())
