import unittest
import uuid
import cache
from client import CachedClient, SourceClient


class TestClient(SourceClient):
    pass


class TestCache(unittest.TestCase):
    def test_cache_on(self):
        cache.set(cache.make_key('42'), 'test')
        self.assertEqual(
            'test',
            cache.get(cache.make_key('42')),
            'Make sure you\'re running memcache')

    def test_cache_on(self):
        cache.set(cache.make_key('42 a'), 'test')
        self.assertEqual(
            'test',
            cache.get(cache.make_key('42 a')),
            'test cached key handling')

    def test_cache_default(self):
        v = cache.get(str(uuid.uuid4()), 'blah')
        self.assertEqual('blah', v)

    def test_from_cache(self):
        TEST_URL = 'http://asdf'

        source_client = TestClient(TEST_URL, 'git')
        source_client.files = ['one.py', 'two.py']
        source_client.discovered = {'name': 'some_project'}
        source_client.cache()

        cached = cache.get(cache.make_key(TEST_URL))
        self.assertIsNotNone(cached)

        client = CachedClient(TEST_URL, cached)
        self.assertEqual(['one.py', 'two.py'], client.files)
        self.assertEqual({'name': 'some_project'}, client.discovered)


if __name__ == '__main__':
    unittest.main()
