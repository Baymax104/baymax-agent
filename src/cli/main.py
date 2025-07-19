# -*- coding: UTF-8 -*-
import asyncio

from cli import user
from cli.menu import Menu
from cli.service import container


async def main():
    await container.init_resources()
    menu = Menu()
    menu.add_item("用户管理", submenu=user.menu)

    await menu.show()
    await container.shutdown_resources()


if __name__ == "__main__":
    asyncio.run(main())
