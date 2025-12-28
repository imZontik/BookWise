import time

from src.core.config import settings
import redis.asyncio as redis

from src.core.observability.metrics import REDIS_OPERATION_SECONDS
from src.domain.cache.protocols import CacheManagerProtocol
from src.infrastructure.cache.manager import RedisCacheManager


class InstrumentedRedis:
    def __init__(self, redis: redis.Redis):
        self._redis = redis

    def __getattr__(self, name: str):
        attr = getattr(self._redis, name)
        if not callable(attr):
            return attr

        async def wrapped(*args, **kwargs):
            start = time.perf_counter()
            try:
                res = await attr(*args, **kwargs)
                REDIS_OPERATION_SECONDS.labels(op=name, status="ok").observe(time.perf_counter() - start)
                return res
            except Exception:
                REDIS_OPERATION_SECONDS.labels(op=name, status="error").observe(time.perf_counter() - start)
                raise

        return wrapped


redis_url = settings.REDIS_URL
redis_client = redis.from_url(redis_url, decode_responses=True)
redis_client = InstrumentedRedis(redis_client)


async def get_redis_cache_manager() -> CacheManagerProtocol:
    return RedisCacheManager(redis_client)