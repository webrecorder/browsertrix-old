from typing import Dict, List
from ujson import loads as ujson_loads

import fakeredis

__all__ = [
    "AwaitFakeRedis",
    "convert_list_str_to_list_dict",
    "init_fake_redis"
]


def convert_list_str_to_list_dict(list_str: List[str]) -> List[Dict]:
    return list(map(ujson_loads, list_str))


class AwaitFakeRedis:
    """ async adapter for fakeredis
    """

    def __init__(self):
        self.redis = fakeredis.FakeStrictRedis(decode_responses=True)

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
