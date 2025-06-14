# -*- coding: UTF-8 -*-
import asyncio
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field


server = FastMCP("calculate")


@server.tool()
def add(
    x: Annotated[int, Field(description="first number")],
    y: Annotated[int, Field(description="second number")]
) -> int:
    """Adds two numbers."""
    return x + y


@server.tool()
def sub(
    x: Annotated[int, Field(description="first number")],
    y: Annotated[int, Field(description="second number")]
) -> int:
    """Subtracts two numbers."""
    return x - y


@server.tool()
def mul(
    x: Annotated[int, Field(description="first number")],
    y: Annotated[int, Field(description="second number")]
) -> int:
    """Multiplies two numbers."""
    return x * y


@server.tool()
def div(
    x: Annotated[int, Field(description="first number")],
    y: Annotated[int, Field(description="second number")]
) -> float:
    """Divides two numbers."""
    return x / y


async def main():
    await server.run_async()


if __name__ == "__main__":
    asyncio.run(main())
