from __future__ import annotations

from redis.asyncio import Redis

_redis: Redis | None = None


async def init_redis(redis_url: str) -> None:
    global _redis
    _redis = Redis.from_url(redis_url, decode_responses=True)


def get_redis() -> Redis:
    if _redis is None:
        raise RuntimeError("Redis not initialized")
    return _redis


async def ping_redis() -> None:
    redis = get_redis()
    await redis.ping()
    replication_info = await redis.info(section="replication")
    if replication_info.get("role") != "master":
        raise RuntimeError(f"Redis replication role is {replication_info.get('role')!r}")


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
