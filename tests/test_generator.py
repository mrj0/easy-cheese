import unittest
from client import SourceClient
from generator import create_setup


class TestClient(SourceClient):
    pass


class TestGenerator(unittest.TestCase):
    def test_packages_for_files(self):
        client = TestClient('http://localhost/repo')
        client.files = [
            'package/one.py',
            'package/__init__.py',
            'py_modules/mod.py',
        ]

        setup = create_setup(client)
        self.assertEqual(['package'], setup.packages.data)
        self.assertEqual(['py_modules.mod'], setup.py_modules.data)

    def test_readme(self):
        client = TestClient('http://localhost/repo')
        client.files = [
            'readme',
            'readme.rst',
            'readme.md',
        ]

        setup = create_setup(client)
        self.assertEqual('readme', setup.readme)

        client.files = [
            'README.rst',
            'readme',
            'readme.md',
        ]

        setup = create_setup(client)
        self.assertEqual('README.rst', setup.readme)

if __name__ == '__main__':
    unittest.main()
