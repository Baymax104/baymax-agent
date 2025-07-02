# -*- coding: UTF-8 -*-
from beanie import init_beanie

from config import Configuration
from monitor import DatabaseError
from users.models import User, UserDB
from utils import AsyncResource, init_mongodb


class UserRepository(AsyncResource):

    def __init__(self, config: Configuration):
        self.config = config.database.mongodb
        self.mongodb = init_mongodb(config.database.mongodb)

    async def initialize(self):
        await init_beanie(self.mongodb[self.config.db], document_models=[UserDB])

    async def add(self, user: User):
        user = user.to_entity()
        await UserDB.insert_one(user)

    async def delete(self, user_id: str):
        user = await UserDB.get(user_id)
        if not user:
            raise DatabaseError(f"User {user_id} not found")
        await user.delete()  # noqa

    async def get(self, user_id: str) -> User | None:
        user = await UserDB.get(user_id)
        return user.to_domain() if user else None

    async def close(self):
        self.mongodb.close()
