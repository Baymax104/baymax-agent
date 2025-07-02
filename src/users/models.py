# -*- coding: UTF-8 -*-
from __future__ import annotations

from uuid import uuid4

from beanie import Document
from pydantic import BaseModel


class User(BaseModel):
    id: str = str(uuid4())
    name: str
    instructions: list[str]

    def to_entity(self) -> UserDB:
        return UserDB.model_validate(self.model_dump())


class UserDB(Document):
    id: str = str(uuid4())
    name: str
    instructions: list[str]


    class Settings:
        name = "User"


    def to_domain(self) -> User:
        return User.model_validate(self.model_dump())
