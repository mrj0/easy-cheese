from itertools import islice
from dulwich.client import HttpGitClient
from dulwich.repo import Repo
import requests
import simplejson as json
from urlparse import urlparse


GITHUB_URL = 'https://api.github.com'


class ClientError(Exception):
    pass


def client_for_url(url):
    if 'github.com' in url:
        return GitHubClient(url)
    if url.startswith('git://') or 'github' in url or url.endswith('.git'):
        return GitClient(url)
    if 'bitbucket.org' in url \
        or 'hg@' in url \
        or 'hg.' in url:
        return HgClient(url)
    raise ValueError('Unsupported url format')


class SourceClient(object):
    def __init__(self, url):
        self.url = url


class DummyGraphWalker(object):
    def ack(self, sha):
        pass

    def next(self):
        pass


def determine_git_wants(refs):
    if 'HEAD' in refs:
        return [refs['HEAD']]
    if 'refs/heads/master' in refs:
        return [refs['refs/heads/master']]
    raise ClientError('The repo doesn\'t have a HEAD or master reference')


def pack_data(data):
    print 'got some data'
    pass


class GitClient(SourceClient):
    def list_files(self):
        # todo need to figure out what to do with a pack file
        #client = HttpGitClient(self.url)
        #client.fetch_pack('/mrj0/jep.git', determine_git_wants,
        # DummyGraphWalker(), pack_data)
        return []


class GitHubClient(SourceClient):
    def __init__(self, url):
        super(GitHubClient, self).__init__(url)
        self.session = requests.session()
        self.session.headers.update({'Accept': 'application/json'})

        path = urlparse(self.url).path
        if not path:
            raise ValueError('Invalid path')
        parts = path.lstrip('/').split('/')
        if not parts or len(parts) < 2:
            raise ValueError('Github url must include a username and repo')

        self.user = parts[0]
        self.repo = parts[1]

        if self.repo.endswith('.git'):
            self.repo = self.repo[:-4]

    def list_files(self):
        request = self.session.request('GET',
            GITHUB_URL +
            '/repos/{}/{}/git/trees/HEAD'.format(
                self.user,
                self.repo,
                ),
            params={'recursive': '1'},
        )

        request.raise_for_status()
        trees = [json.loads(request.content)]
        files = []

        i = 0
        while i < len(trees):
            obj = trees[i]

            if isinstance(obj, list):
                for child in obj:
                    if isinstance(child, dict) and child.get('type') == 'blob':
                        files.append(child['path'])

            if 'tree' in obj:
                trees.append(obj['tree'])
            i += 1
        return files


class HgClient(SourceClient):
    pass
