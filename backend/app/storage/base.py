from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageBackend(ABC):
    @abstractmethod
    async def put(self, key: str, content: BinaryIO, content_type: str = "") -> str:
        pass

    @abstractmethod
    async def get(self, key: str) -> bytes | None:
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass
