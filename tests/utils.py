from typing import Any, Callable, Dict, List, Optional, Set
from ujson import loads as ujson_loads

import fakeredis

__all__ = [
    'AwaitFakeRedis',
    'convert_list_str_to_list',
    'convert_list_str_to_set',
    'init_fake_redis',
]

PropSelector = Callable[[Dict], Any]


def convert_list_str_to_list(
    list_str: List[str], prop_selector: Optional[PropSelector] = None
) -> List[Any]:
    if prop_selector is None:
        return list(map(ujson_loads, list_str))
    return list(map(lambda x: prop_selector(ujson_loads(x)), list_str))


def convert_list_str_to_set(
    list_str: List[str], prop_selector: Optional[PropSelector] = None
) -> Set[Any]:
    if prop_selector is None:
        return set(map(ujson_loads, list_str))
    return set(map(lambda x: prop_selector(ujson_loads(x)), list_str))


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
