# -*- coding: UTF-8 -*-
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Literal

from fastmcp.utilities.mcp_config import MCPConfig, RemoteMCPServer, StdioMCPServer
from pydantic import BaseModel, ConfigDict, field_validator


class BaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True)


class ModelConfig(BaseConfig):
    provider: str | None = None
    model: str | None = None
    api_key: str | None = None
    generation: dict[str, Any] | None = None


class BaseInstanceConfig(BaseConfig, ABC):
    name: str
    description: str

    @abstractmethod
    def to_mcp(self) -> StdioMCPServer | RemoteMCPServer:
        ...


class StdioInstanceConfig(BaseInstanceConfig):
    script: str
    args: list[str] = []
    env: dict[str, Any] = {}
    cwd: str | None = None

    def to_mcp(self) -> StdioMCPServer:
        # check script
        root = Path(__file__).parent.parent / "servers"
        script_path = Path(self.script)
        if not script_path.is_absolute():
            script_path = (root / self.script).resolve()
        if not script_path.is_file():
            raise FileNotFoundError(f"Script not found: {script_path}")
        if not str(script_path).endswith(".py"):
            raise ValueError(f"Not a Python script: {script_path}")

        full_args = [str(script_path)]
        if self.args:
            full_args.extend(self.args)
        return StdioMCPServer(
            command=sys.executable,
            args=full_args,
            env=self.env,
            cwd=self.cwd
        )


class RemoteInstanceConfig(BaseInstanceConfig):
    url: str
    headers: dict[str, str] = {}
    auth: str | Literal["oauth"] | None = None

    def to_mcp(self) -> RemoteMCPServer:
        return RemoteMCPServer(
            url=self.url,
            headers=self.headers,
            auth=self.auth,
        )


class ServerConfig(BaseConfig):
    instances: list[StdioInstanceConfig | RemoteInstanceConfig]

    def to_mcp(self) -> MCPConfig:
        mcp_servers = {
            server_config.name: server_config.to_mcp()
            for server_config in self.instances
        }
        return MCPConfig(mcpServers=mcp_servers)


class LogConfig(BaseConfig):
    dir: str | None = None

    @field_validator("dir")
    @classmethod
    def dir_validator(cls, value: str) -> str:
        value = Path(value)
        if not value.is_absolute():
            value = Path(__file__).parent.parent.parent / value
        return str(value.resolve())



class Configuration(BaseConfig):
    env: Literal["dev", "prod"]
    model: ModelConfig = ModelConfig()
    log: LogConfig = LogConfig()
    server: ServerConfig = ServerConfig(instances=[])
