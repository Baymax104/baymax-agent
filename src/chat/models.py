# -*- coding: UTF-8 -*-
import time
from typing import Literal
from uuid import uuid4

from beanie import Document
from pydantic import BaseModel


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
