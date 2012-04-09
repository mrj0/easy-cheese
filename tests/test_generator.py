import unittest
import os
from client import SourceClient, TemporaryDirectory
import client
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
        self.assertEqual('package', setup.packages.data)
        self.assertEqual('py_modules.mod', setup.py_modules.data)

    def test_readme(self):
        client = TestClient('http://localhost/repo')
        client.files = [
            'readme',
            'readme.rst',
            'readme.md',
        ]

        setup = create_setup(client)
        self.assertEqual('readme', setup.readme.data)

        client.files = [
            'README.rst',
            'readme',
            'readme.md',
        ]

        setup = create_setup(client)
        self.assertEqual('README.rst', setup.readme.data)

    def test_no_requirements(self):
        """
        Make sure generation doesn't fail with
        missing or invalid requirements files.
        """
        with TemporaryDirectory() as temp:
            test_client = TestClient('http://localhost/repo')
            test_client.files = [
                'readme.rst',
                'requirements.txt',
                ]

            with open(os.path.join(temp.name, 'requirements.txt'), 'w') as f:
                f.write('-r adsf')

            client._find_requires(test_client, temp.name)
            setup = create_setup(test_client)
            self.assertEqual('readme.rst', setup.readme.data)
            self.assertEqual([], setup.requires.data)

    def test_requirements(self):
        with TemporaryDirectory() as temp:
            test_client = TestClient('http://localhost/repo')
            test_client.files = [
                'readme.rst',
                'requirements.txt',
                ]

            with open(os.path.join(temp.name, 'requirements.txt'), 'w') as f:
                f.write('''
Jinja2==2.6
MarkupSafe>=0.15
WTForms
''')

            client._find_requires(test_client, temp.name)
            setup = create_setup(test_client)
            self.assertEqual('readme.rst', setup.readme.data)
            self.assertEqual(['Jinja2==2.6',
                              'MarkupSafe>=0.15',
                              'WTForms'], setup.requires.data)

if __name__ == '__main__':
    unittest.main()
