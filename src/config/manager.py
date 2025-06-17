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

        all_config = cls.all_config.as_dict()
        configuration = {
            "env": all_config["ENV"],
            "model": all_config["MODEL"],
            "server": all_config["SERVER"]
        }
        configuration = Configuration.model_validate(configuration)
        return configuration

    @classmethod
    def __init_config(cls) -> Configuration:
        servers = [
            StdioInstanceConfig(name="", description="", script=""),
            RemoteInstanceConfig(name="", description="", url=""),
        ]
        configuration = Configuration(
            env="dev",
            model=ModelConfig(api_key="@get api_key"),
            server=ServerConfig(instances=servers)
        )
        return configuration

