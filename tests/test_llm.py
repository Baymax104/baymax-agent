# -*- coding: UTF-8 -*-
from langchain_core.messages import BaseMessage, HumanMessage
from pytest import mark

from client.llm import LLMFactory
from config import ModelConfig


test_llm_config = [
    ("zhipuai", "glm-4-flash", "<KEY>"),
    ("deepseek", "deepseek-chat", "<KEY>")
]


@mark.parametrize("provider, model, api_key", test_llm_config)
def test_llm(provider, model, api_key):
    model_config = ModelConfig(
        provider=provider,
        model=model,
        api_key=api_key,
    )

    llm = LLMFactory.create(model_config)
    messages: list[BaseMessage] = [HumanMessage("Hello")]
    message = llm.generate(messages)
    print(message)
