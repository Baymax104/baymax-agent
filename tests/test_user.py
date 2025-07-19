# -*- coding: UTF-8 -*-
from pytest import mark

from injection import Container


container = Container()


@mark.asyncio
async def test_user_service():
    await container.init_resources()
    service = container.user.service()
    user_id = await service.add("test", [])

    user = await service.get(user_id)
    assert user.id == user_id

    all_users = await service.get_all()
    assert len(all_users) == 1

    user_by_name = await service.get_by_name("test")
    assert user_by_name.id == user_id

    await service.delete(user_id)
    await container.shutdown_resources()
