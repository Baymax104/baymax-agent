# -*- coding: UTF-8 -*-
from uuid import uuid4

from beanie import Document


class User(Document):
    id: str = str(uuid4())
    name: str
    instructions: list[str]
