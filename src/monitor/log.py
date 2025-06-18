# -*- coding: UTF-8 -*-
import sys
from pathlib import Path

from loguru import logger as __logger

from config import ConfigManager, Configuration


def init(config: Configuration):
    __logger.remove(0)

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "{message}"
    )

    if config.env == "prod":
        log_dir = Path(config.log.dir)
        log_dir.mkdir(exist_ok=True)
        __logger.add(
            log_dir / "monitor.log",
            format=log_format,
            encoding="utf-8",
            rotation="20s",
            retention="30min",
            enqueue=True,
        )
    else:
        __logger.add(sys.stdout, format=log_format, level="DEBUG", colorize=True)

    return __logger


logger = init(ConfigManager.get_config())
