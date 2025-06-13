# -*- coding: UTF-8 -*-
from pathlib import Path

from config import ConfigManager


test_config_path = Path(__file__).parent / "config.yml"
ConfigManager.config_path = test_config_path


def test_get_config():
    config_ = ConfigManager.get_config()
    print(config_)

