# -*- coding: UTF-8 -*-
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class BaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True)


class APIConfig(BaseConfig):
    api_key: str | None = None
    base_url: str | None = None


class StdioServerConfig(BaseConfig):
    command: str
    args: list[str] = []
    env: dict[str, Any] = {}
    cwd: str | None = None


class RemoteServerConfig(BaseConfig):
    url: str
    headers: dict[str, str] = {}
    auth: str | Literal["oauth"] | None = None


class ServerConfig(BaseConfig):
    default: str | None = None
    instances: dict[str, StdioServerConfig | RemoteServerConfig]


class Configuration(BaseConfig):
    api: APIConfig = APIConfig()
    server: ServerConfig
