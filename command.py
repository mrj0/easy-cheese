import subprocess
import threading
import settings
import logging

log = logging.getLogger(__name__)


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

        if self.process and\
           self.process.returncode is not None and\
           self.process.returncode != 0:

            log.error('Command failed: args={} kwargs={}'.format(
                self.args, self.kwargs))
            raise CommandException(
                'Command returned a non-zero status {}'.format(
                    self.process.returncode))

        return self.communicate
