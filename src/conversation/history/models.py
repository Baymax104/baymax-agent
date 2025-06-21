# -*- coding: UTF-8 -*-
from langchain_core.messages import AnyMessage
from pydantic import BaseModel, ConfigDict


class Conversation(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str
    user_id: str
    create_timestamp: float
    messages: list[AnyMessage]
