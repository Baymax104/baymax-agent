# -*- coding: UTF-8 -*-
from beanie import Document
from beanie.exceptions import CollectionWasNotInitialized
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis

from config import MongoDBConfig, RedisConfig


def init_mongodb(config: MongoDBConfig) -> AsyncIOMotorClient:
    if not config.host or not config.port:
        raise ConnectionError("Host and port are required.")
    if not config.db:
        raise ConnectionError("Database is required.")
    user_part = f"{config.user}:{config.password}@" if config.user else ""
    uri = f"mongodb://{user_part}{config.host}:{config.port}"
    client = AsyncIOMotorClient(uri)
    return client


def init_redis(config: RedisConfig) -> Redis:
    if not config.host or not config.port:
        raise ConnectionError("Host and port are required.")
    db = config.db if config.db else 0
    redis = Redis(
        host=config.host,
        port=config.port,
        password=config.password,
        db=db,
    )
    return redis


def is_connected(doc_type: type[Document]) -> bool:
    try:
        doc_type.get_settings()
        return True
    except CollectionWasNotInitialized:
        return False
