import unittest
import cache
from client import CachedClient, SourceClient


class TestClient(SourceClient):
    pass


class TestCache(unittest.TestCase):
    def test_cache_on(self):
        cache.set('42', 'test')
        self.assertEqual('test', cache.get('42'))

    def test_from_cache(self):
        TEST_URL = 'http://asdf'

        source_client = TestClient(TEST_URL)
        source_client.files = ['one.py', 'two.py']
        source_client.discovered = {'name': 'some_project'}
        source_client.cache()

        cached = cache.get(TEST_URL)
        self.assertIsNotNone(cached)

        client = CachedClient(TEST_URL, cached)
        self.assertTrue(client.from_cache)
        self.assertEqual(['one.py', 'two.py'], client.files)
        self.assertEqual({'name': 'some_project'}, client.discovered)


if __name__ == '__main__':
    unittest.main()
