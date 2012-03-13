import unittest
from client import client_for_url, GitClient, HgClient, GitHubClient


class TestGitClient(unittest.TestCase):
    def test_simple(self):
        # known remote protocol formats
        c = client_for_url('ssh://user@server:project.git')
        self.assertIsInstance(c, GitClient)
        c = client_for_url('user@server:project.git')
        self.assertIsInstance(c, GitClient)
        c = client_for_url('ssh://hg@bitbucket.org/richardjones/python-sword2')
        self.assertIsInstance(c, HgClient)

    def test_list_files(self):
        client = client_for_url('http://github.com/mrj0/jep.git')
        self.assertIsInstance(client, GitHubClient)
        self.assertEqual(93, len(client.list_files()))

if __name__ == '__main__':
    unittest.main()
