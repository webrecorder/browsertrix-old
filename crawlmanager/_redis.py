from asyncio import AbstractEventLoop

from aioredis import Redis, create_redis

__all__ = ["init_redis"]


async def init_redis(redis_url: str, loop: AbstractEventLoop) -> Redis:
    return await create_redis(redis_url, encoding="utf-8", loop=loop)

