# -*- coding: UTF-8 -*-
from redis import Redis

from config import ConfigManager, Configuration


class RedisClient:

    def __init__(self, config: Configuration):
        self.config = config.database.redis
        self.prefix = "agent"
        self.redis = Redis(
            host=self.config.host,
            port=self.config.port,
            db=self.config.db,
            password=self.config.password,
        )

    def get(self, key: str) -> bytes:
        key = f"{self.prefix}:{key}"
        return self.redis.get(key)

    def set(self, key: str, value: bytes) -> bool:
        key = f"{self.prefix}:{key}"
        return self.redis.set(key, value)

    def delete(self, key: str) -> bool:
        key = f"{self.prefix}:{key}"
        return self.redis.delete(key)

    def exists(self, key: str) -> bool:
        key = f"{self.prefix}:{key}"
        return self.redis.exists(key)


redis_db = RedisClient(ConfigManager.get_config())
