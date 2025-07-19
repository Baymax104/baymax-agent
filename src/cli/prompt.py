# -*- coding: UTF-8 -*-
from typing import Any

from rich import get_console
from rich.box import ROUNDED
from rich.table import Table


__console = get_console()


def success(message: str):
    __console.print(f"[green]{message}[/green]")


def error(message: str):
    __console.print(f"[red]{message}[/red]")


def info(rich_text: str):
    __console.print(rich_text)


def print_list(items: list[Any], **table_config):
    if not items:
        return
    table = Table(**table_config, box=ROUNDED)
    table.add_column()

    if len(items) == 1:
        table.add_row(f"[green][1][/] {items[0]}")
        __console.print(table)
        return

    table.add_column()
    for i in range(0, len(items), 2):
        item1 = f"[green][{i + 1}][/] {items[i]}"
        item2 = f"[green][{i + 2}][/] {items[i + 1]}" if i + 1 < len(items) else ""
        table.add_row(item1, item2)
    __console.print(table)


def print_dict(d: dict[str, Any], **table_config):
    table = Table(**table_config, box=ROUNDED)
    table.add_column()
    table.add_column()
    for key, value in d.items():
        table.add_row(f"[cyan]{key.capitalize()}", str(value))
    __console.print(table)
