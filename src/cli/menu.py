# -*- coding: UTF-8 -*-
from __future__ import annotations

import asyncio
from typing import Callable

from rich import get_console
from rich.box import ROUNDED
from rich.prompt import Prompt
from rich.table import Table


class Menu:

    def __init__(
        self,
        title: str = "主菜单",
        back_option: bool = True,
        exit_option: bool = True,
    ):
        """
        Args:
            title: 菜单标题
            back_option: 是否显示返回上级菜单选项
            exit_option: 是否显示退出程序选项
        """
        self.title = title
        self.items = []
        self.submenus = {}
        self.back_option = back_option
        self.exit_option = exit_option
        self.parent = None
        self.actions = {}
        self.console = get_console()
        # 样式配置
        self.style = {
            "item": "white",
            "selected": "bold green",
            "error": "bold red",
            "back": "yellow",
            "exit": "red"
        }

    def add_item(
        self,
        label: str,
        *,
        action: Callable | None = None,
        submenu: Menu | None = None
    ) -> Menu:
        """
        添加菜单项

        Args:
            label: 菜单项显示文本
            action: 菜单项选中时执行的函数
            submenu: 关联的子菜单

        Returns:
            当前菜单实例，支持链式调用
        """
        item_id = len(self.items) + 1
        self.items.append((item_id, label))

        if action:
            self.actions[item_id] = action
        elif submenu:
            submenu.parent = self
            self.submenus[item_id] = submenu

        return self

    def action(self, label: str) -> Callable:
        def decorator(action: Callable | None) -> Callable:
            self.add_item(label, action=action)
            return action

        return decorator

    async def show(self) -> None:
        """显示菜单并处理用户选择"""
        while True:
            self._print_menu()
            choice = await self._get_valid_choice()

            if choice == -1:  # 返回上级菜单
                if self.parent:
                    return
                else:
                    self.console.print("已经是顶级菜单", style=self.style["error"])
                    continue
            elif choice == 0:  # 退出程序
                return

            # 处理菜单项选择
            if choice in self.submenus:
                await self.submenus[choice].show()
            elif choice in self.actions:
                try:
                    action = self.actions[choice]
                    if asyncio.iscoroutinefunction(action):
                        await action()
                    else:
                        action()
                    input("Press any key to exit...")
                except Exception as e:
                    self.console.print(f"Error: {e}", style=self.style["error"])
                    input("Press any key to exit...")

    def _print_menu(self):
        self.console.clear()

        # 创建菜单项表格
        table = Table(
            title=self.title,
            show_header=False,
            show_lines=False,
            style=self.style["item"],
            box=ROUNDED
        )
        table.add_column(justify="right", width=3)
        table.add_column(justify="left")

        for item_id, label in self.items:
            table.add_row(f"[{self.style['selected']}]{item_id}[/]", label)

        # 添加返回和退出选项
        if self.back_option and self.parent:
            table.add_row(f"[{self.style['back']}]-1[/]", "返回上级菜单")

        if self.exit_option and not self.parent:
            table.add_row(f"[{self.style['exit']}]0[/]", "退出程序")

        self.console.print(table)
        self.console.print()

    async def _get_valid_choice(self) -> int:
        """获取并验证用户输入"""
        valid_choices = [str(item[0]) for item in self.items]

        if self.back_option and self.parent:
            valid_choices.append("-1")

        if self.exit_option:
            valid_choices.append("0")

        while True:
            choice = Prompt.ask("请输入选择", choices=valid_choices, show_choices=False)
            return int(choice)
