import pylibmc
import settings
import hashlib

_client = pylibmc.Client(settings.MEMCACHE_SERVERS,
                         username=settings.MEMCACHE_USERNAME,
                         password=settings.MEMCACHE_PASSWORD,
                         behaviors={"tcp_nodelay": True})


def make_key(value):
    return hashlib.sha256(value).hexdigest()


def get(key, default=None):
    """
    Get a cache value.

    ``key`` must be passed through ``make_key``
    ``default`` value if not present
    """

    value = _client.get(key)
    if value is not None:
        return value
    return default


def set(key, value, time=172800):
    """
    Set the cache value.

    ``key`` must be from ``make_key``
    ``value`` to cache
    ``time`` defaults to 2 days in seconds.
    """

    return _client.set(key, value, time=time)
