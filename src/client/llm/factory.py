# -*- coding: UTF-8 -*-
from client.llm.base import LLMProvider
from client.llm.deepseek import DeepSeek
from client.llm.zhipuai import ZhipuAI
from config import ModelConfig


class LLMFactory:
    __providers = {
        "zhipuai": ZhipuAI,
        "deepseek": DeepSeek,
    }

    __registry: dict[str, LLMProvider] = {}

    @classmethod
    def create(cls, config: ModelConfig) -> LLMProvider:
        provider = config.provider
        if provider is None:
            raise ValueError(f"Missing provider")
        if provider not in cls.__providers:
            raise NotImplementedError(f"Provider {provider} is not implemented")
        if provider not in cls.__registry:
            llm_cls = cls.__providers[provider]
            cls.__registry[provider] = llm_cls(config)
        return cls.__registry[provider]
