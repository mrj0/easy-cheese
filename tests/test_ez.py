import unittest
from easycheese import clean_packages


class TestEZ(unittest.TestCase):
    def test_clean_packages(self):
        self.assertEqual(['one', 'two'], clean_packages('one, two'))
        self.assertEqual(['one', 'two'], clean_packages('one two'))
        self.assertEqual(['one', 'two9'], clean_packages('one two9'))
        self.assertEqual(['one', 'two', 'three'], clean_packages('one two\nthree'))


if __name__ == '__main__':
    unittest.main()
