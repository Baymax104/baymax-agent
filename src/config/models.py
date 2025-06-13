# -*- coding: UTF-8 -*-
import sys
from pathlib import Path
from typing import Any, Literal

from fastmcp.utilities.mcp_config import MCPConfig, RemoteMCPServer, StdioMCPServer
from pydantic import BaseModel, ConfigDict, RootModel


class BaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True)


class ModelConfig(BaseConfig):
    provider: str | None = None
    model: str | None = None
    api_key: str | None = None
    generation: dict[str, Any] | None = None


class StdioServerConfig(BaseConfig):
    script: str
    args: list[str] = []
    env: dict[str, Any] = {}
    cwd: str | None = None

    def to_mcp(self) -> StdioMCPServer:
        # check script
        root = Path(__file__).parent.parent / "servers"
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


class RemoteServerConfig(BaseConfig):
    url: str
    headers: dict[str, str] = {}
    auth: str | Literal["oauth"] | None = None

    def to_mcp(self) -> RemoteMCPServer:
        return RemoteMCPServer(**self.model_dump())


class ServerConfig(RootModel):
    root: dict[str, StdioServerConfig | RemoteServerConfig]

    def to_mcp(self) -> MCPConfig:
        mcp_servers = {
            server: server_config.to_mcp()
            for server, server_config in self.root.items()
        }
        return MCPConfig(mcpServers=mcp_servers)



class Configuration(BaseConfig):
    model: ModelConfig = ModelConfig()
    servers: ServerConfig = ServerConfig(root={})
