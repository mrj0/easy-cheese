#from dulwich.client import HttpGitClient
#from dulwich.name import Repo
import os
import requests
import simplejson as json
from urlparse import urlparse
import settings


class ClientError(Exception):
    pass


class ClientTimeoutError(Exception):
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
        self.author = None
        self.email = None
        self.name = None
        self.description = None
        self.version = None
        self.long_description = None
        self.files = []


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
    raise ClientError('The name doesn\'t have a HEAD or master reference')


def pack_data(data):
    print 'got some data'
    pass


class GitClient(SourceClient):
    def fetch(self):
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

        self.author = parts[0]
        self.name = parts[1]

        if self.name.endswith('.git'):
            self.name = self.name[:-4]

    def fetch(self):
        """
        Perform remote request to get repo details
        """

        try:
            url = settings.GITHUB_URL + '/repos/{}/{}'.format(
                self.author,
                self.name,
            )

            request = self.session.request(
                'get',
                url,
                timeout=settings.SOURCE_TIMEOUT,
            )
        except requests.Timeout:
            raise ClientTimeoutError('Timeout while reading from Github\'s repo API')

        request.raise_for_status()
        repo = json.loads(request.content)
        self.url = repo['homepage']
        self.description = repo['description']

        try:
            url = settings.GITHUB_URL + '/repos/{}/{}/git/trees/HEAD'.format(
                self.author,
                self.name,
            )

            request = self.session.request(
                'get',
                url,
                params={'recursive': '1'},
                timeout=settings.SOURCE_TIMEOUT,
            )
        except requests.Timeout:
            raise ClientTimeoutError('Timeout while reading from Github\'s git API')

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
        self.files = files
        return files


class HgClient(SourceClient):
    pass
