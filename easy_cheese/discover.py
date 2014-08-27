import os
import re
from urllib.parse import urlsplit
from pip.req import parse_requirements
from easy_cheese.commands import shell


def _to_id(v):
    return str(v).replace('-', '_').replace('/', '.').replace('.py', '')


def packages_in(path):
    """
    return all the packages in ``path``

    :param path:
    :return:
    """
    for init in path.glob('**/__init__.py'):
        yield _to_id(init.relative_to(path).parent)


def immediate_packages_in(path):
    """
    return all the packages in ``path`` (not including subdirs)

    :param path:
    :return:
    """
    for init in path.glob('*/__init__.py'):
        yield _to_id(init.relative_to(path).parent)


def project_name(path):
    packages = list(immediate_packages_in(path))

    root_name = _to_id(path.name)

    # if there is a package matching root, that's most likely the name
    # as in, easy-cheese/easy_cheese
    if root_name in packages:
        return path.name

    # otherwise, return a top-level package, if found
    if packages:
        return str(list(packages)[0])


def git_author_name(path):
    return shell('git log -1 --pretty=format:%an').stdout.strip()


def git_author_email(path):
    return shell('git log -1 --pretty=format:%ae').stdout.strip()


def git_project_url(path):
    # remote urls look like: git@github.com:mrj0/easy-cheese.git
    # or possibly: https://github.com/mrj0/easy-cheese.git
    # or https://github.com/mrj0/easy-cheese
    result = shell('git remote -v show')

    for line in result.stdout.split('\n'):
        name, remote, _ = re.split(r'\s', line.strip())
        print('remote', remote)

        if remote.startswith('git@github'):
            _host, path = remote.split(':')
            path = path.replace('.git', '')
            organization, project = os.path.split(path)
            return 'https://github.com/{}/{}'.format(organization, project)

        if remote.startswith('https://github'):
            path = urlsplit(remote).path
            path = path.replace('.git', '')
            organization, project = os.path.split(path)
            return 'https://github.com/{}/{}'.format(organization.lstrip('/'), project)


def requirements(path):
    """
    Look for a requirements file and discover ``requires``
    """
    discovered = []
    for found in path.glob('*require*.txt'):
        for req in parse_requirements(str(found)):
            discovered.append(str(req.req))

    if discovered:
        return discovered


def modules(path):
    return [_to_id(p.name) for p in path.glob('*.py') if p.name != 'setup.py']


def entry_points(path):
    entries = []
    for abspy in path.glob('**/*.py'):
        with open(str(abspy), 'rb') as f:
            source = f.read().decode()

        if '__main__' in source:
            script = _to_id(abspy.relative_to(path))
            name = script.split('.')[-1]
            entries.append('{} = {}:main'.format(name, script))

    if entries:
        return {'console_scripts': entries}
