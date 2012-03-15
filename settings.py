
DEBUG = True

MERCURIAL_BIN = '/usr/local/bin/hg'

GIT_BIN = '/usr/local/bin/git'

GITHUB_URL = 'https://api.github.com'

MEMCACHED_HOST = 'localhost'
MEMCACHED_PORT = 11211

SOURCE_TEMP = '/tmp/ez'

# timeout to fetch repos
SOURCE_TIMEOUT = 30

try:
    from local_settings import *
except:
    pass
