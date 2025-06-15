# -*- coding: UTF-8 -*-
from pathlib import Path

from dynaconf import Dynaconf
from ruamel.yaml import YAML

from config.models import Configuration, ModelConfig, RemoteInstanceConfig, ServerConfig, StdioInstanceConfig


class ConfigManager:
    context_root: Path = Path(__file__).parent.parent.parent
    config_path: Path = context_root / "config.yml"
    all_config: Dynaconf = Dynaconf(
        root_path=context_root,
        settings_files=[config_path.name, ".secrets.*"],
    )

    @classmethod
    def get_config(cls) -> Configuration:
        if not cls.config_path.exists():
            configuration = cls.__init_config()
            with cls.config_path.open("w", encoding="utf-8") as f:
                YAML().dump(configuration.model_dump(), f)
            return configuration

        configuration = {"model": cls.all_config.model, "server": cls.all_config.server}
        configuration = Configuration.model_validate(configuration)
        return configuration

    @classmethod
    def __init_config(cls) -> Configuration:
        servers = [
            StdioInstanceConfig(name="", description="", script=""),
            RemoteInstanceConfig(name="", description="", url=""),
        ]
        configuration = Configuration(
            model=ModelConfig(api_key="@get api_key"),
            server=ServerConfig(instances=servers)
        )
        return configuration

