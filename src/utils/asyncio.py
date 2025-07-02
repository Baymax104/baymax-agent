# -*- coding: UTF-8 -*-
from abc import ABC, abstractmethod
from typing import Self


class AsyncResource(ABC):

    @abstractmethod
    async def initialize(self):
        ...

    @abstractmethod
    async def close(self):
        ...

    async def __aenter__(self) -> Self:
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
