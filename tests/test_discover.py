import mock
from pathlib import Path, PurePath
from unittest import TestCase
from easy_cheese import discover
from easy_cheese.commands import CommandResult


class TestDiscover(TestCase):
    def setUp(self):
        self.root = Path(__file__).parent.parent

    def test_project_name(self):
        self.assertEqual('easy-cheese', discover.project_name(self.root))

    @mock.patch.object(Path, 'glob')
    def test_project_different_package(self, glob):
        glob.return_value = iter([self.root / 'other/__init__.py'])
        self.assertEqual('other', discover.project_name(self.root))

    @mock.patch.object(discover, 'shell')
    def test_project_git_author(self, shell):
        shell.return_value = CommandResult('mud', None, 0)
        self.assertEqual('mud', discover.git_author_name(Path.cwd()))

    @mock.patch.object(discover, 'shell')
    def test_project_git_author_email(self, shell):
        shell.return_value = CommandResult('mud', None, 0)
        self.assertEqual('mud', discover.git_author_email(Path.cwd()))

    @mock.patch.object(discover, 'shell')
    def test_project_git_url(self, shell):
        shell.return_value = CommandResult('origin	git@github.com:mrj0/easy-cheese.git (fetch)', None, 0)
        self.assertEqual('https://github.com/mrj0/easy-cheese', discover.git_project_url(Path.cwd()))

        shell.return_value = CommandResult('origin	https://github.com/mrj0/easy-cheese.git (fetch)', None, 0)
        self.assertEqual('https://github.com/mrj0/easy-cheese', discover.git_project_url(Path.cwd()))

        shell.return_value = CommandResult('origin	https://github.com/mrj0/easy-cheese (fetch)', None, 0)
        self.assertEqual('https://github.com/mrj0/easy-cheese', discover.git_project_url(Path.cwd()))

    @mock.patch.object(Path, 'glob')
    def test_console_scripts(self, path):
        path.return_value = [
            self.root / 'setup.py',
            self.root / 'easy_cheese/commands.py',
            self.root / 'easy_cheese/main.py',
            self.root / 'easy_cheese/trove.py',
            self.root / 'easy_cheese/__init__.py',
        ]

        entry_points = discover.entry_points(self.root)
        self.assertEqual({
            'console_scripts': [
                'main = easy_cheese.main:main',
            ]}, entry_points)
