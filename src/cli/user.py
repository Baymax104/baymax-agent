# -*- coding: UTF-8 -*-
from rich.prompt import Prompt

from cli.menu import Menu
from cli.prompt import error, print_dict, print_list, success
from cli.service import container
from users import UserService


menu = Menu("用户管理")


@menu.action("创建用户")
async def add_user():
    service: UserService = container.user.service()
    username = Prompt.ask("请输入用户名")
    exist_user = await service.get_by_name(username)
    if exist_user:
        error(f"用户\"{username}\"已存在")
        return
    await service.add(username, [])
    success(f"用户\"{username}\"创建成功")


@menu.action("用户列表")
async def list_user():
    service: UserService = container.user.service()
    users = await service.get_all()
    user_infos = [f"[cyan]{user.name}[/]({user.id})" for user in users]
    print_list(user_infos, title="用户列表", show_header=False)


@menu.action("查看用户")
async def display_user():
    service: UserService = container.user.service()
    users = await service.get_all()
    user_infos = [f"[cyan]{user.name}[/]({user.id})" for user in users]
    print_list(user_infos, title="用户列表", show_header=False)
    username = Prompt.ask("请输入用户名")
    user = next((user for user in users if user.name == username), None)
    if not user:
        error(f"User {username} not found")
        return
    print_dict(user.model_dump(), title="用户信息", show_header=False)


@menu.action("删除用户")
async def delete_user():
    service: UserService = container.user.service()
    users = await service.get_all()
    user_infos = [f"[cyan]{user.name}[/]({user.id})" for user in users]
    print_list(user_infos, title="用户列表", show_header=False)
    username = Prompt.ask("请输入用户名")
    user = next((user for user in users if user.name == username), None)
    if not user:
        error(f"User {username} not found")
        return
    await service.delete(user.id)
    success(f"用户\"{user.name}\"删除成功")
