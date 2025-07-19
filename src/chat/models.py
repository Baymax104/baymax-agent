# -*- coding: UTF-8 -*-
from __future__ import annotations

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


class ConversationDB(Document):
    id: str = str(uuid4())
    user_id: str
    title: str
    type: str
    create_at: float = time.time()
    content: list[ChatTurn] = []


    class Settings:
        name = "Conversation"


    def to_domain(self) -> Conversation:
        return Conversation.model_validate(self.model_dump())


class Conversation(BaseModel):
    id: str = str(uuid4())
    user_id: str
    title: str
    type: str
    create_at: float = time.time()
    content: list[ChatTurn] = []

    def to_entity(self) -> ConversationDB:
        return ConversationDB.model_validate(self.model_dump())
