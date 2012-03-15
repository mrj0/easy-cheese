import pylibmc
import settings

_client = pylibmc.Client(['{}:{}'.format(settings.MEMCACHED_HOST,
                                         settings. MEMCACHED_PORT)],
                         behaviors={"tcp_nodelay": True})

def get(key):
    return _client.get(key)


def set(key, value):
    return _client.set(key, value)
