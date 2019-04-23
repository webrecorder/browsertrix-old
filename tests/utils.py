from typing import Any, Callable, Dict, List, Optional, Set
import json

import fakeredis

__all__ = [
    'AwaitFakeRedis',
    'init_fake_redis',
]


class AwaitFakeRedis:
    """ async adapter for fakeredis
    """

    def __init__(self):
        self.redis = fakeredis.FakeStrictRedis(decode_responses=True)

    def close(self):
        self.redis.close()

    def __getattr__(self, name):
        async def func(*args, **kwargs):
            return getattr(self.redis, name)(*args, **kwargs)

        return func

    async def iscan(self, match=None, count=None):
        for key in self.redis.scan_iter(match=match, count=count):
            yield key

    async def hmset_dict(self, key, kwargs):
        return self.redis.hmset(key, kwargs)


async def init_fake_redis(*args, **kwargs) -> AwaitFakeRedis:
    return AwaitFakeRedis()
