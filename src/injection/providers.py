# -*- coding: UTF-8 -*-
from contextlib import asynccontextmanager

from beanie import init_beanie
from fastmcp import Client as MCPClient
from fastmcp.client.transports import MCPConfigTransport
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis

from chat import ConversationDB
from config import Configuration
from llm import LLMFactory
from users.models import UserDB


@asynccontextmanager
async def provide_llm(config: Configuration):
    llm = LLMFactory.create(config.model)
    await llm.initialize()
    yield llm


@asynccontextmanager
async def provide_mcp_client(config: Configuration):
    client = MCPClient(MCPConfigTransport(config.server.to_mcp()), timeout=10)
    try:
        client = await client.__aenter__()
        yield client
    finally:
        await client.close()


@asynccontextmanager
async def provide_mongodb(config: Configuration):
    config = config.database.mongodb
    if not config.host or not config.port:
        raise ConnectionError("Host and port are required.")
    if not config.db:
        raise ConnectionError("Database is required.")
    user_part = f"{config.user}:{config.password}@" if config.user else ""
    uri = f"mongodb://{user_part}{config.host}:{config.port}"
    client = AsyncIOMotorClient(uri)
    await init_beanie(client[config.db], document_models=[ConversationDB, UserDB])
    yield client
    client.close()


@asynccontextmanager
async def provide_redis(config: Configuration):
    config = config.database.redis
    if not config.host or not config.port:
        raise ConnectionError("Host and port are required.")
    db = config.db if config.db else 0
    redis = Redis(
        host=config.host,
        port=config.port,
        password=config.password,
        db=db,
    )
    await redis.initialize()
    yield redis
    await redis.aclose()
