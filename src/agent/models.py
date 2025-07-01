# -*- coding: UTF-8 -*-
from typing import AsyncIterator

from langchain_core.messages import AnyMessage, BaseMessage
from pydantic import BaseModel, ConfigDict


class ChatState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    middle: list[AnyMessage] = []
    stream: AsyncIterator[AnyMessage] | None = None


class Session(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    context: list[BaseMessage]
    user_instructions: list[str] = []
