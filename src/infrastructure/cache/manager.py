import json
from json import JSONDecodeError
from typing import Optional, Any

from src.domain.cache.protocols import CacheManagerProtocol

import redis.asyncio as redis


class RedisCacheManager(CacheManagerProtocol):
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    async def get(self, key: str) -> Optional[str]:
        try:
            return await self.redis_client.get(key)
        except Exception:
            return None

    async def set(
            self,
            key: str,
            value: str,
            ttl: int
    ) -> None:
        if ttl <= 0:
            return

        try:
            await self.redis_client.set(key, value, ex=ttl)
        except Exception:
            pass

    async def delete(self, key: str) -> None:
        try:
            await self.redis_client.delete(key)
        except Exception:
            pass

    async def get_json(self, key: str) -> Optional[Any]:
        raw = await self.get(key)

        if raw is None:
            return None

        try:
            return json.loads(raw)
        except JSONDecodeError:
            await self.delete(key)
            return None

    async def set_json(
            self,
            key: str,
            value: Any,
            ttl: int
    ) -> None:
        if ttl <= 0:
            return

        try:
            raw = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        except Exception:
            return

        await self.set(key, raw, ttl)