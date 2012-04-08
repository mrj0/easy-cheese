from datetime import datetime
from fabric.decorators import hosts
import os

from fabric.api import sudo, cd, env

GIT_URL = "git://github.com/mrj0/easy-cheese.git"
DEPLOYED = '/opt/deployed/{}'
DEPLOYED_DIR = '/opt/deployed'


def run(cmd, user=None, **kwargs):
    if not user:
        user = env.sv_account
    return sudo(cmd, user=user, **kwargs)


def _setup():
    env.sv_account = 'ezcheese'
    env.deploy = DEPLOYED.format(
        datetime.today().isoformat().replace(':', '_'))
    env.project = '{}/project'.format(env.deploy)


@hosts('ezcheese.mrj0.com')
def deploy():
    _setup()

    create_virtualenv()
    clone_source()
    install_requirements()

    symlink_current()

    restart_gunicorn()
    restart_memcached()


def current_env():
    """
    Get the path to the virtualenv currently in use
    """
    current = DEPLOYED.format('current')
    link = run('readlink -f {}'.format(current))
    print 'current env', env.deploy
    return link


def symlink_current():
    current = DEPLOYED.format('current')
    run('rm -f {}'.format(current))
    run('ln -s {} {}'.format(env.deploy, current))


def create_virtualenv():
    run('virtualenv -p /usr/bin/python2.7 ' \
        '--prompt=ezcheese ' \
        '--distribute {deploy}'.format(**env))


@hosts('ezcheese.mrj0.com')
def cleanup():
    _setup()

    current = os.path.basename(current_env())
    old_entries = set(run('ls -1 {}'.format(DEPLOYED_DIR)).splitlines()) - \
        {'current', current}
    if old_entries:
        with cd(DEPLOYED_DIR):
            run('rm -rf {}'.format(' '.join(old_entries)))


def virtualenv(command):
    with cd(env.project):
        run('source {deploy}/bin/activate && {command}'.format(
            command=command,
            deploy=env.deploy))


def clone_source():
    run('git clone --depth=1 {} {project}'.format(GIT_URL, **env))


def install_requirements():
    run('PIP_DOWNLOAD_CACHE=~{sv_account}/.pip_cache ' \
        '{deploy}/bin/pip install ' \
        '--use-mirrors ' \
        '-r {project}/requirements.txt'.format(**env))


def restart_memcached():
    run('echo "flush_all" | nc localhost 11211')


def restart_gunicorn():
    sudo('kill `cat /opt/gunicorn/pid`')
