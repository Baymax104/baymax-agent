# -*- coding: UTF-8 -*-
from config import ModelConfig
from llm.base import LLMProvider
from llm.deepseek import DeepSeek
from llm.zhipuai import ZhipuAI
from monitor import ConfigInvalidError, LLMProviderError, logger


class LLMFactory:
    __providers = {
        "zhipuai": ZhipuAI,
        "deepseek": DeepSeek,
    }

    __registry: dict[str, LLMProvider] = {}

    @classmethod
    @logger.catch_exception(throw=True)
    def create(cls, config: ModelConfig) -> LLMProvider:
        provider = config.provider
        if provider is None:
            raise ConfigInvalidError(f"Missing provider")
        if provider not in cls.__providers:
            raise LLMProviderError(f"Provider {provider} is not implemented")
        if provider not in cls.__registry:
            llm_cls = cls.__providers[provider]
            cls.__registry[provider] = llm_cls(config)
        return cls.__registry[provider]
