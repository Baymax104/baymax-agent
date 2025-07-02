# -*- coding: UTF-8 -*-
from pytest import mark

from config import ConfigManager
from users.service import UserService


@mark.asyncio
async def test_user_service():
    config = ConfigManager.get_config()
    async with UserService(config) as service:
        user_id = await service.add("test", [])
        user = await service.get(user_id)
        assert user.id == user_id
        await service.delete(user_id)
