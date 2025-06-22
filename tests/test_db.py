# -*- coding: UTF-8 -*-
import ormsgpack
from icecream import ic
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from conversation import Session


def test_messagepack():
    session = Session(
        id="111",
        context=[
            SystemMessage("Hello"),
            HumanMessage("你好"),
            AIMessage("hello", tool_calls=[{"name": "hello", "args": {}, "id": "abc"}]),
            ToolMessage("你好", tool_call_id="abc")
        ]
    )
    ic(session)
    session = ormsgpack.packb(session.model_dump())
    ic(type(session), session)

    session = ormsgpack.unpackb(session)
    session = Session.model_validate(session)
    ic(session)


def test_redis():
    from db.redis import redis_db
    redis_db.set("hello", b"world")
    is_exist = redis_db.exists("hello")
    assert is_exist
    value = redis_db.get("hello")
    assert value == b"world"
    assert redis_db.delete("hello")
    assert not redis_db.exists("hello")
