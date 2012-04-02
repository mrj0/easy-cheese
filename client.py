import shutil
import tempfile
import threading
import os
from pip.exceptions import InstallationError
from pip.req import parse_requirements
import re
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


class ClientTimeoutError(ClientError):
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

    if 'bitbucket.org' in url:
        return BitbucketClient(url)

    if url.startswith('git://') or url.endswith('.git'):
        return GitClient(url)

    raise ValueError('Unsupported url format')


class TemporaryDirectory(object):

    def __init__(self, name=None):
        self.name = name
        if not self.name:
            self.name = tempfile.mkdtemp()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self.name)


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

        self.communicate = ()

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
    def __init__(self, url):
        self.url = url
        self.files = []
        self.discovered = {}

        # options for parse_requirements
        self.skip_requirements_regex = '^(-r|--requirement)'
        self.default_vcs = 'git'

        log.info('%s with client URL "%s"', type(self), self.url)

    def _temp_directory(self):
        tmp = settings.SOURCE_TEMP
        if not os.path.exists(tmp):
            os.mkdir(tmp, 0700)
        return TemporaryDirectory(tempfile.mkdtemp(dir=tmp))

    def cache(self):
        cache.set(cache.make_key(self.url), {
            'files': self.files,
            'discovered': self.discovered,
        })

    def _find_requires(self, dir):
        """
        Look for a requirements file and discover ``requires``
        """
        pn = re.compile(r'.*require.*\.txt$', re.I)
        requires = []

        for root, dirs, files in os.walk(dir):
            for filename in files:
                if re.match(pn, filename):
                    try:
                        for req in parse_requirements(
                                os.path.join(dir, root, filename),
                                options=self):
                            requires.append(str(req.req))
                    except InstallationError:
                        log.exception('ignored')

        self.discovered['requires'] = requires


class MercurialClient(SourceClient):

    def __init__(self, url):
        super(MercurialClient, self).__init__(url)
        self.default_vcs = 'hg'

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

            self._find_requires(out_dir)


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

            response = self.session.request(
                'get',
                url,
                timeout=settings.API_TIMEOUT,
            )
        except requests.Timeout:
            raise ClientTimeoutError('Timeout while reading from '
                                     'Bitbuckets\'s repo API')

        if response.status_code != 200:
            raise ClientError('Server error {0}'.format(response.status_code))

        repo = json.loads(response.content)

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

            self._find_requires(out_dir)


class GitHubClient(GitClient):
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

            response = self.session.request(
                'get',
                url,
                timeout=settings.API_TIMEOUT,
            )
        except requests.Timeout:
            raise ClientTimeoutError('Timeout while reading from '
                                     'Github\'s repo API')

        if response.status_code != 200:
            raise ClientError('Server error {0}'.format(response.status_code))

        repo = json.loads(response.content)
        self.discovered['url'] = repo['homepage']
        self.discovered['description'] = repo['description']

        super(GitHubClient, self).fetch()


class CachedClient(SourceClient):

    def __init__(self, url, cached):
        super(CachedClient, self).__init__(url)

        self.files = cached.get('files', [])
        self.discovered = cached.get('discovered', {})

    def fetch(self):
        pass

    def cache(self):
        pass
