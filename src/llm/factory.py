# -*- coding: UTF-8 -*-
from config import ModelConfig
from llm.base import LLMProvider
from llm.deepseek import DeepSeek
from llm.zhipuai import ZhipuAI


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
