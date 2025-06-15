# -*- coding: UTF-8 -*-
from pathlib import Path

from config import ConfigManager


test_config_path = Path(__file__).parent / "config.yml"
ConfigManager.config_path = test_config_path


def test_get_config():
    config_ = ConfigManager.get_config()
    print(config_)


def test_secret_config():
    from dynaconf import Dynaconf
    settings = Dynaconf(
        root_path=Path(__file__).parent.parent,
        settings_file=["config.yml", ".secrets.*"],
    )
    settings = settings.as_dict()
    print(settings)
