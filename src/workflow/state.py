# -*- coding: UTF-8 -*-
from langchain_core.messages import AnyMessage, ToolCall
from pydantic import BaseModel, ConfigDict


class State(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    messages: list[AnyMessage]


class ToolState(State):
    server: str | None = None
    tool_calls: list[ToolCall] = []
