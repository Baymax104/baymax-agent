# -*- coding: UTF-8 -*-
import time
from typing import Literal
from uuid import uuid4

from beanie import Document
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, ConfigDict


class Message(BaseModel):
    role: Literal["human", "ai"]
    content: str


class ChatTurn(BaseModel):
    human_message: Message
    ai_message: Message


class Conversation(Document):
    id: str = str(uuid4())
    user_id: str
    title: str
    type: Literal["archive", "temporary"]
    create_at: float = time.time()
    content: list[ChatTurn] = []


class Session(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    context: list[BaseMessage]
    user_instructions: list[str] = []
