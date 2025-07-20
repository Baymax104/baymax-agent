# -*- coding: UTF-8 -*-
import asyncio

from cli.chat_item import menu as chat_menu
from cli.container import container
from cli.menu import Menu
from cli.user_item import menu as user_menu


async def main():
    await container.init_resources()
    menu = Menu()
    menu.add_item("用户管理", submenu=user_menu)
    menu.add_item("对话管理", submenu=chat_menu)

    await menu.show()
    await container.shutdown_resources()


if __name__ == "__main__":
    asyncio.run(main())
