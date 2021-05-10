from os import environ
from urllib.parse import urlsplit

from aioredis import Redis, create_redis
from ujson import loads

from .types_ import EnvType, EnvValue, Loop, OptionalAny

__all__ = ['env', 'extract_domain', 'init_redis']


async def init_redis(redis_url: str, loop: Loop) -> Redis:
    return await create_redis(redis_url, encoding='utf-8', loop=loop)


def env(key: str, type_: EnvType = str, default: OptionalAny = None) -> EnvValue:
    """Returns the value of the supplied env key name converting
    the env key's value to the specified type.

    If the env key does not exist the default value is returned.

    Boolean values for env keys are expected to be:
      - true: 1, true, yes, y, ok, on
      - false: 0, false, no, n, nok, off

    :param key: The name of the environment variable
    :param type_: What type should the the env key's value be converted to,
    defaults to str
    :param default: The default value of the env key, defaults to None
    :return: The value of the env key or the supplied default
    """
    if key not in environ:
        return default

    val = environ[key]

    if type_ == str:
        return val
    elif type_ == bool:
        if val.lower() in ['1', 'true', 'yes', 'y', 'ok', 'on']:
            return True
        if val.lower() in ['0', 'false', 'no', 'n', 'nok', 'off']:
            return False
        raise ValueError(
            f'Invalid environment variable "{key}" (expected a boolean): "{val}"'
        )
    elif type_ == int:
        try:
            return int(val)
        except ValueError:
            raise ValueError(
                f'Invalid environment variable "{key}" (expected a integer): "{val}"'
            )
    elif type_ == float:
        try:
            return float(val)
        except ValueError:
            raise ValueError(
                f'Invalid environment variable "{key}" (expected a float): "{val}"'
            )
    elif type_ == dict:
        return loads(val)


def extract_domain(url: str) -> str:
    """Extracts and returns the domain, including the suffix,
    of the supplied URL

    :param url: The url to have its domain extracted from
    :return: The extracted domain
    """
    extracted = urlsplit(url).netloc
    return extracted.replace('www.', '')
