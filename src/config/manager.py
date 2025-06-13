# -*- coding: UTF-8 -*-
from pathlib import Path

from ruamel.yaml import YAML

from config.models import Configuration, RemoteServerConfig, ServerConfig, StdioServerConfig


class ConfigManager:
    config_path: Path = Path(__file__).parent.parent.parent / "config.yml"

    @classmethod
    def get_config(cls) -> Configuration:
        if not cls.config_path.exists():
            configuration = cls.__init_config()
            with cls.config_path.open("w", encoding="utf-8") as f:
                YAML().dump(configuration.model_dump(), f)
            return configuration

        with cls.config_path.open("r", encoding="utf-8") as f:
            configuration = YAML().load(f)
        configuration = Configuration.model_validate(configuration)
        return configuration

    @classmethod
    def __init_config(cls) -> Configuration:
        servers = {
            "stdio_server_name": StdioServerConfig(script=""),
            "remote_server_name": RemoteServerConfig(url=""),
        }
        configuration = Configuration(servers=ServerConfig(root=servers))
        return configuration


if __name__ == "__main__":
    c = ConfigManager.get_config()
    print(c)
