import os
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s %(asctime)s %(pathname)s:%(lineno)d %(message)s')


DEBUG = True

MERCURIAL_BIN = '/usr/bin/hg'

GIT_BIN = '/usr/bin/git'

GITHUB_URL = 'https://api.github.com'

BITBUCKET_URL = 'https://api.bitbucket.org/1.0'

# how long to wait for a clone in seconds
CLONE_TIMEOUT = 60

MEMCACHE_SERVERS = [os.environ.get('MEMCACHE_SERVERS', 'localhost:11211')]
MEMCACHE_USERNAME = os.environ.get('MEMCACHE_USERNAME')
MEMCACHE_PASSWORD = os.environ.get('MEMCACHE_PASSWORD')

SOURCE_TEMP = '/tmp/ez'

# timeout to fetch repos
API_TIMEOUT = 30

try:
    from local_settings import *
except ImportError:
    pass
