# -*- coding: UTF-8 -*-
from typing import Callable, Protocol, cast

from config import ConfigManager, Configuration
from monitor.log import logger


class ExceptionCollector:

    def __init__(self, config: Configuration):
        self.__registered_methods: dict[str, Callable] = {}
        self.env = config.env

    def register(self, method: Callable, throw: bool = False) -> Callable:
        method_name = method.__qualname__

        def wrapper(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except Exception as e:
                self.__handle(e, method_name)
                if throw:
                    raise e

        self.__registered_methods[method_name] = wrapper
        return wrapper

    def __handle(self, e: Exception, method_name: str):
        error_name = e.__class__.__name__
        if self.env == "prod":
            logger.error(f"{error_name} | {method_name}: {str(e)}")
        else:
            logger.exception(f"Exception occurred in <{method_name}>", exception=e)


# for type hint
class Logger(Protocol):
    def catch_exception(self, *, throw: bool = False) -> Callable: ...


exception_collector = ExceptionCollector(ConfigManager.get_config())


def catch_exception(*, throw: bool = False) -> Callable:
    def decorator(func: Callable) -> Callable:
        return exception_collector.register(func, throw=throw)

    return decorator


logger.catch_exception = catch_exception
logger = cast(Logger, logger)
