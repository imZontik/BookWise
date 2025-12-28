from typing import Protocol, Optional, Any


class CacheManagerProtocol(Protocol):
    async def get(self, key: str) -> Optional[str]: ...
    async def delete(self, key: str) -> None: ...

    async def set(
            self,
            key: str,
            value: str,
            ttl: int
    ) -> None: ...

    async def get_json(self, key: str) -> Optional[Any]: ...

    async def set_json(
            self,
            key: str,
            value: Any,
            ttl: int
    ) -> None: ...