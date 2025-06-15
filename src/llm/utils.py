# -*- coding: UTF-8 -*-
from typing import Any

from mcp import Tool


def convert_to_openai_tools(tools: list[Tool]) -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        }
        for tool in tools
    ]
