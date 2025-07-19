# -*- coding: UTF-8 -*-

from monitor import DatabaseError
from users.models import User, UserDB


class UserRepository:

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

    async def get_all(self) -> list[User]:
        all_user = await UserDB.find_all().to_list()
        all_user = [user.to_domain() for user in all_user]
        return all_user

    async def get_by_name(self, name: str) -> User | None:
        user = await UserDB.find_one({"name": name})
        return user.to_domain() if user else None
