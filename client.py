import shutil
import tempfile
import threading
import os
import requests
import simplejson as json
from urlparse import urlparse
import cache
import settings
import subprocess
import logging


log = logging.getLogger(__name__)


class ClientError(Exception):
    pass


class ClientTimeoutError(Exception):
    pass


def client_for_url(url, repo_type=None):
    if repo_type == 'git':
        if 'github.com' in url:
            return GitHubClient(url)
        return GitClient(url)

    if repo_type == 'hg':
        if 'bitbucket.org' in url:
            return BitbucketClient(url)
        return MercurialClient(url)

    if 'github.com' in url:
        return GitHubClient(url)

    if url.startswith('git://') or url.endswith('.git'):
        return GitClient(url)

    if 'bitbucket.org' in url \
        or 'hg@' in url \
        or 'hg.' in url:
        return HgClient(url)
    raise ValueError('Unsupported url format')


class TemporaryDirectory(object):

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.name)


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


class CommandException(Exception):
    pass


class CommandTimeoutException(Exception):
    pass


class Command(object):
    def __init__(self, *args, **kwargs):
        self.process = None
        self.args = args
        self.kwargs = kwargs
        self.thread = None

        self.timeout = self.kwargs.pop('timeout', settings.CLONE_TIMEOUT)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        try:
            if self.process:
                self.process.kill()
        except OSError:
            pass
        except Exception:
            log.exception('failed to kill process')

        if self.thread:
            self.thread.join()

    def run(self):
        def target():
            try:
                log.info('popen args=%s kwargs=%s', self.args, self.kwargs)

                self.kwargs['stdout'] = subprocess.PIPE
                self.kwargs['stdin'] = subprocess.PIPE
                self.process = subprocess.Popen(*self.args, **self.kwargs)
                self.communicate = self.process.communicate()
            except Exception:
                log.exception('thread exception')

        self.thread = threading.Thread(target=target)
        self.thread.start()
        self.thread.join(self.timeout)

        if self.thread.is_alive():
            log.error('Terminating process')
            self.process.kill()
            raise CommandTimeoutException()

        if self.process and \
           self.process.returncode is not None and \
           self.process.returncode != 0:

            log.error('Command failed: args={} kwargs={}'.format(
                self.args, self.kwargs))
            raise CommandException(
                'Command returned a non-zero status {}'.format(
                    self.process.returncode))

        return self.communicate


class SourceClient(object):
    def __init__(self, url, from_cache=False):
        self.from_cache = from_cache
        self.url = url
        self.files = []
        self.discovered = {}

        log.info('%s with client URL "%s"', type(self), self.url)

    def _temp_directory(self):
        tmp = settings.SOURCE_TEMP
        if not os.path.exists(tmp):
            os.mkdir(tmp, mode=0700)
        return TemporaryDirectory(tempfile.mkdtemp(dir=tmp))

    def cache(self):
        if not self.from_cache:
            cache.set(self.url, {
                'files': self.files,
                'discovered': self.discovered,
            })


class MercurialClient(SourceClient):

    def __init__(self, url):
        super(MercurialClient, self).__init__(url)

        if not settings.DEBUG:
            if self.url.startswith('/'):
                raise ClientError('File urls not allowed')

    def fetch(self):
        with self._temp_directory() as tmpdir:

            out_dir = os.path.join(tmpdir.name, 'hg')
            try:
                subprocess.check_call([
                    settings.MERCURIAL_BIN,
                    'clone',
                    str(self.url),
                    out_dir,
                ])
            except subprocess.CalledProcessError:
                log.exception('Failed to clone mercurial repo')

            for root, dirs, files in os.walk(out_dir):
                if '.hg' in dirs:
                    dirs.remove('.hg')

                for file in files:
                    self.files.append(os.path.join(root, file).replace(
                        out_dir, '', 1).lstrip('/'))


class BitbucketClient(MercurialClient):
    def __init__(self, url):
        super(BitbucketClient, self).__init__(url)
        self.session = requests.session()
        self.session.headers.update({'Accept': 'application/json'})

        path = urlparse(self.url).path
        if not path:
            raise ValueError('Invalid path')
        parts = path.lstrip('/').split('/')
        if not parts or len(parts) < 2:
            raise ValueError('Bitbucket url must include a username and repo')

        self.author = parts[0]
        self.name = parts[1]

        if not self.name or not self.author:
            raise ValueError('Error parsing URL. Ensure the URL contains the'
                             'username and repo on Bitbucket.')

        self.discovered['author'] = self.author
        self.discovered['name'] = self.name

    def fetch(self):
        try:
            url = settings.BITBUCKET_URL + '/repositories/{}/{}'.format(
                self.author,
                self.name,
            )

            request = self.session.request(
                'get',
                url,
                timeout=settings.API_TIMEOUT,
            )
        except requests.Timeout:
            raise ClientTimeoutError('Timeout while reading from '
                                     'Bitbuckets\'s repo API')

        request.raise_for_status()
        repo = json.loads(request.content)

        self.discovered['description'] = repo['description']
        self.discovered['url'] = repo['website']

        if 'fork_of' in repo:
            self.discovered['description'] = repo['fork_of']['description']
            self.discovered['url'] = repo['fork_of']['website']

        super(BitbucketClient, self).fetch()


class GitClient(SourceClient):

    def __init__(self, url):
        super(GitClient, self).__init__(url)

        if not settings.DEBUG:
            if self.url.startswith('/'):
                raise ClientError('File urls not allowed')

    def fetch(self):
        with self._temp_directory() as tmpdir:

            out_dir = os.path.join(tmpdir.name, 'git')
            try:
                subprocess.check_call([
                    settings.GIT_BIN,
                    'clone',
                    '--depth',
                    '1',
                    str(self.url),
                    out_dir,
                ])
            except subprocess.CalledProcessError:
                log.exception('Failed to clone git repo')

            for root, dirs, files in os.walk(out_dir):
                if '.git' in dirs:
                    dirs.remove('.git')

                for file in files:
                    self.files.append(os.path.join(root, file).replace(
                        out_dir, '', 1).lstrip('/'))


class GitHubClient(SourceClient):
    def __init__(self, url):
        super(GitHubClient, self).__init__(url)
        self.session = requests.session()
        self.session.headers.update({'Accept': 'application/json'})

        if '://' in self.url:
            # handle urls with schemes

            path = urlparse(self.url).path
            if not path:
                raise ValueError('Invalid path')
            parts = path.lstrip('/').split('/')
            if not parts or len(parts) < 2:
                raise ValueError('Github url must include a username and repo')

            self.author = parts[0]
            self.name = parts[1]
        else:
            # no scheme, this breaks urlparse

            parts = self.url.split(':')[-1]
            if not parts or '/' not in parts:
                raise ValueError('Github url must include a username and repo')

            parts = parts.split('/')
            if len(parts) < 2:
                raise ValueError('Github url must include a username and repo')

            self.author = parts[0]
            self.name = parts[1]

        if self.name.endswith('.git'):
            self.name = self.name[:-4]

        if not self.name or not self.author:
            raise ValueError('Error parsing URL. Ensure the URL contains the'
                             'username and repo on Github.')

        self.discovered['author'] = self.author
        self.discovered['name'] = self.name

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
                timeout=settings.API_TIMEOUT,
            )
        except requests.Timeout:
            raise ClientTimeoutError('Timeout while reading from '
                                     'Github\'s repo API')

        request.raise_for_status()
        repo = json.loads(request.content)
        self.discovered['url'] = repo['homepage']
        self.discovered['description'] = repo['description']

        try:
            url = settings.GITHUB_URL + '/repos/{}/{}/git/trees/HEAD'.format(
                self.author,
                self.name,
            )

            request = self.session.request(
                'get',
                url,
                params={'recursive': '1'},
                timeout=settings.API_TIMEOUT,
            )
        except requests.Timeout:
            raise ClientTimeoutError('Timeout while reading from '
                                     'Github\'s git API')

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


class HgClient(SourceClient):
    pass


class CachedClient(SourceClient):

    def __init__(self, url, cached):
        super(CachedClient, self).__init__(url, from_cache=True)

        self.files = cached.get('files', [])
        self.discovered = cached.get('discovered', {})

    def fetch(self):
        pass
