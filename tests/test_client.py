import unittest
from client import client_for_url, GitClient, HgClient, GitHubClient


class TestClient(unittest.TestCase):
    def test_simple(self):
        # known remote protocol formats
        c = client_for_url('ssh://author@server:project.git')
        self.assertIsInstance(c, GitClient)
        c = client_for_url('author@server:project.git')
        self.assertIsInstance(c, GitClient)
        c = client_for_url('ssh://hg@bitbucket.org/richardjones/python-sword2')
        self.assertIsInstance(c, HgClient)

        c = client_for_url('https://mrj0@github.com/mrj0/jep.git')
        self.assertIsInstance(c, GitHubClient)
        c = client_for_url('git@github.com:mrj0/jep.git')
        self.assertIsInstance(c, GitHubClient)

    def test_github_client_git(self):
        c = client_for_url('git@github.com:mrj0/jep.git')
        self.assertIsInstance(c, GitHubClient)
        self.assertEqual('mrj0', c.author)

        self.assertRaises(ValueError, client_for_url, 'git@github.com:mrj0')
        self.assertRaises(ValueError, client_for_url, 'git@github.com:mrj0/')

    def test_github_client_https(self):
        c = client_for_url('https://mrj0@github.com/mrj0/jep.git')
        self.assertIsInstance(c, GitHubClient)
        self.assertEqual('mrj0', c.author)

        self.assertRaises(ValueError, client_for_url, 'https://mrj0@github.com/mrj0/')


#    def test_list_files(self):
#        client = client_for_url('http://github.com/mrj0/jep.git')
#        self.assertIsInstance(client, GitHubClient)
#        self.assertEqual(93, len(client.fetch()))

if __name__ == '__main__':
    unittest.main()
