# -*- coding: UTF-8 -*-
from config import Configuration
from monitor import get_logger
from users import User
from users.repository import UserRepository
from utils import AsyncResource


logger = get_logger()


class UserService(AsyncResource):

    def __init__(self, config: Configuration):
        self.config = config
        self.repo = UserRepository(config)

    async def initialize(self):
        await self.repo.initialize()

    async def add(self, username: str, instructions: list[str]) -> str:
        user = User(name=username, instructions=instructions)
        await self.repo.add(user)
        logger.debug(f"Created user {user.id}")
        return user.id

    @logger.catch_exception(throw=True)
    async def delete(self, user_id: str):
        await self.repo.delete(user_id)
        logger.debug(f"Deleted user {user_id}")

    async def get(self, user_id: str) -> User | None:
        return await self.repo.get(user_id)

    async def close(self):
        await self.repo.close()
