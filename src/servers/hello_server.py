# -*- coding: UTF-8 -*-
import asyncio

from fastmcp import FastMCP


server = FastMCP("hello")


@server.tool()
def ping() -> str:
    return "Hello World!"


async def main():
    await server.run_async()


if __name__ == "__main__":
    asyncio.run(main())
