# -*- coding: UTF-8 -*-

from langchain_core.messages import BaseMessage, HumanMessage
from pytest import mark

from config import ModelConfig
from llm import LLMFactory


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


@mark.parametrize("provider, model, api_key", test_llm_config)
def test_llm_stream(provider, model, api_key):
    model_config = ModelConfig(
        provider=provider,
        model=model,
        api_key=api_key,
    )

    llm = LLMFactory.create(model_config)
    messages: list[BaseMessage] = [HumanMessage("Hello")]
    for chunk in llm.generate(messages, stream=True):
        print(chunk)


@mark.asyncio
@mark.parametrize("provider, model, api_key", test_llm_config)
async def test_llm_async(provider, model, api_key):
    model_config = ModelConfig(
        provider=provider,
        model=model,
        api_key=api_key,
    )
    llm = LLMFactory.create(model_config)
    messages: list[BaseMessage] = [HumanMessage("Hello")]

    message = await llm.generate_async(messages)
    print(message)


@mark.asyncio
@mark.parametrize("provider, model, api_key", test_llm_config)
async def test_llm_async_stream(provider, model, api_key):
    model_config = ModelConfig(
        provider=provider,
        model=model,
        api_key=api_key,
    )
    llm = LLMFactory.create(model_config)
    messages: list[BaseMessage] = [HumanMessage("Hello")]

    async for chunk in await llm.generate_async(messages, stream=True):
        print(chunk)
