import subprocess


class CommandResult(object):
    def __init__(self, stdout, stderr, returncode):
        self.stdout = stdout
        self.stderr = stderr
        self.exitcode = self.returncode = returncode
        self.failed = False
        self.succeeded = True


class CommandFailed(Exception):
    def __init__(self, command, result):
        self.command = command
        self.result = result
        super(CommandFailed, self).__init__()


def shell(command):
    """
    Run a local shell command and wait for output. From fabric's local command

    """
    out_stream = subprocess.PIPE
    err_stream = subprocess.PIPE
    p = subprocess.Popen(command, shell=True, stdout=out_stream, stderr=err_stream)
    stdout, stderr = p.communicate()

    result = CommandResult(
        stdout.decode().strip() if stdout else "",
        stderr.decode().strip() if stderr else "",
        p.returncode,
    )

    if p.returncode != 0:
        raise CommandFailed(command, result)
    return result
