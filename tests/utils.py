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
        """
        Initialize the redis connection.

        Args:
            self: (todo): write your description
        """
        self.redis = fakeredis.FakeStrictRedis(decode_responses=True)

    def close(self):
        """
        Close the connection.

        Args:
            self: (todo): write your description
        """
        self.redis.close()

    def __getattr__(self, name):
        """
        Get an attribute from the cache.

        Args:
            self: (todo): write your description
            name: (str): write your description
        """
        async def func(*args, **kwargs):
              """
              Decorator for a function

              Args:
              """
            return getattr(self.redis, name)(*args, **kwargs)

        return func

    async def iscan(self, match=None, count=None):
          """
          Incrementally iterate the set.

          Args:
              self: (todo): write your description
              match: (todo): write your description
              count: (int): write your description
          """
        for key in self.redis.scan_iter(match=match, count=count):
            yield key

    async def hmset_dict(self, key, kwargs):
          """
          Emulate hmset hash.

          Args:
              self: (todo): write your description
              key: (str): write your description
          """
        return self.redis.hmset(key, kwargs)


async def init_fake_redis(*args, **kwargs) -> AwaitFakeRedis:
      """
      Initialize a redis instance.

      Args:
      """
    return AwaitFakeRedis()
