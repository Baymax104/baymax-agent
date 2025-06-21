# -*- coding: UTF-8 -*-
from __future__ import annotations

import sys
import types
from pathlib import Path
from typing import Callable, cast

from loguru import logger as __logger
from loguru._logger import Logger as LoguruLogger

from config import ConfigManager, Configuration
from monitor.collector import catch_exception


# for type hint
class Logger(LoguruLogger):
    def catch_exception(self, *, throw: bool = False) -> Callable: pass


def init(config: Configuration, service: str | None = None) -> Logger:
    log_config = config.log
    service = "monitor" if not service else service
    __logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "{message}"
    )

    if config.env == "prod":
        log_dir = Path(log_config.dir)
        log_dir.mkdir(exist_ok=True)
        __logger.add(
            log_dir / f"{service}.log",
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

    logger = __logger.bind(service=service)

    logger.catch_exception = types.MethodType(catch_exception, logger)
    logger = cast(Logger, logger)

    return logger


def get_logger(service: str | None = None) -> Logger:
    return init(ConfigManager.get_config(), service=service)
