# -*- coding: UTF-8 -*-
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class BaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True)


class ModelConfig(BaseConfig):
    provider: str | None = None
    model: str | None = None
    api_key: str | None = None
    generation: dict[str, Any] | None = None


class StdioServerConfig(BaseConfig):
    command: str
    args: list[str] = []
    env: dict[str, Any] = {}
    cwd: str | None = None


class RemoteServerConfig(BaseConfig):
    url: str
    headers: dict[str, str] = {}
    auth: str | Literal["oauth"] | None = None


class Configuration(BaseConfig):
    model: ModelConfig = ModelConfig()
    servers: dict[str, StdioServerConfig | RemoteServerConfig]
