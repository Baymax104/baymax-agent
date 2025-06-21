# -*- coding: UTF-8 -*-
from langchain_core.messages import AnyMessage
from pydantic import BaseModel, ConfigDict


class Session(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str
    context: list[AnyMessage]
    user_instructions: list[str] = []
