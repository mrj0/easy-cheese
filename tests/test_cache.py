import unittest
import cache

class TestCache(unittest.TestCase):
    def test_cache_on(self):
        cache.set('42', 'test')
        self.assertEqual('test', cache.get('42'))

if __name__ == '__main__':
    unittest.main()
