# -*- coding: UTF-8 -*-
from monitor import get_logger
from users.models import User
from users.repository import UserRepository


logger = get_logger()


class UserService:

    def __init__(self, repository: UserRepository):
        self.repo = repository

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

    async def get_all(self) -> list[User]:
        return await self.repo.get_all()

    async def get_by_name(self, name: str) -> User | None:
        return await self.repo.get_by_name(name)
