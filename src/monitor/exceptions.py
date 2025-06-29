# -*- coding: UTF-8 -*-
from typing import Any


class BaseError(Exception):
    message: str
    context: dict[str, Any] | None = None

    def __init__(self, message: str):
        self.message = message


class AgentError(BaseError):
    pass


class ConfigError(BaseError):
    pass


class ConfigNotFoundError(ConfigError):
    pass


class ConfigInvalidError(ConfigError):
    pass


class LLMError(BaseError):
    pass


class LLMProviderError(LLMError):
    pass


class LLMConnectionError(LLMError):
    pass


class MCPError(BaseError):
    pass


class MCPConnectionError(MCPError):
    pass


class MCPToolError(MCPError):
    pass


class DatabaseError(BaseError):
    pass


class ConversationError(BaseError):
    pass


class ConversationNotFoundError(ConversationError):
    pass
