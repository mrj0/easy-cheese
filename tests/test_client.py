import unittest
from command import Command, CommandTimeoutException


class TestClient(unittest.TestCase):
#    def test_github_client_git(self):
#        c = client_for_url('git@github.com:mrj0/jep.git')
#        self.assertIsInstance(c, GitHubClient)
#        self.assertEqual('mrj0', c.author)
#
#        self.assertRaises(ValueError, client_for_url, 'git@github.com:mrj0')
#        self.assertRaises(ValueError, client_for_url, 'git@github.com:mrj0/')
#
#    def test_github_client_https(self):
#        c = client_for_url('https://mrj0@github.com/mrj0/jep.git')
#        self.assertIsInstance(c, GitHubClient)
#        self.assertEqual('mrj0', c.author)
#
#        self.assertRaises(ValueError, client_for_url, 'https://mrj0@github.com/mrj0/')

    def test_command(self):
        with Command('echo hello', shell=True) as cmd:
            self.assertEqual('hello', cmd.run()[0].strip())

        with Command(['sleep', '100000'], timeout=.1) as cmd:
            self.assertRaises(CommandTimeoutException, cmd.run)


#    def test_list_files(self):
#        client = client_for_url('http://github.com/mrj0/jep.git')
#        self.assertIsInstance(client, GitHubClient)
#        self.assertEqual(93, len(client.fetch()))

if __name__ == '__main__':
    unittest.main()
