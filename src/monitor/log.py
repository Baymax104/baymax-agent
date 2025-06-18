# -*- coding: UTF-8 -*-
import sys
from pathlib import Path

from loguru import logger as __logger

from config import ConfigManager, Configuration


def init(config: Configuration):
    log_config = config.log
    __logger.remove(0)

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "{message}"
    )

    if config.env == "prod":
        log_dir = Path(log_config.dir)
        log_dir.mkdir(exist_ok=True)
        __logger.add(
            log_dir / "monitor.log",
            format=log_format,
            encoding="utf-8",
            level=log_config.level,
            rotation=log_config.rotation,
            retention=log_config.retention,
            enqueue=True,
        )
    else:
        __logger.add(
            sys.stdout,
            format=log_format,
            level=log_config.level,
            colorize=True
        )

    return __logger


logger = init(ConfigManager.get_config())
