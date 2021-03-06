from fabric.api import (
    cd,
    env,
    prefix,
    require,
    run,
    sudo,
    task,
)
from logging import (
    addLevelName,
    basicConfig,
    getLogger,
    Logger,
    StreamHandler,
)
from fabric.contrib import console
from fabric.utils import abort
from textwrap import dedent
import sys
from datetime import datetime
from atexit import register
from phabricator import Phabricator
from StringIO import StringIO
from io import IOBase


class IOLogger(IOBase):
    def __init__(self, level='NOTE'):
        super(IOLogger, self).__init__(self)

        self.level = level

        # Grab logger output
        self.log_io = StringIO()

        # Grab console output
        self.console_io = StringIO()

        # Own the buffers
        sys.stdout = sys.stdin = sys.stderr = self

        self.note_level = 25
        addLevelName(
            self.note_level,
            'NOTE',
        )
        Logger.note = self.note

        basicConfig(
            level=self.level,
            stream=self.log_io,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        )

        console_io_handler = StreamHandler(stream=self.console_io)
        self.output_logger = getLogger('fabric.output')
        self.input_logger = getLogger('fabric.input')
        self.output_logger.addHandler(console_io_handler)
        self.input_logger.addHandler(console_io_handler)

    def note(self, message, *args, **kws):
        self._log(
            self.note_level,
            message,
            *args,
            **kws
        )

    '''StringIO does not use file descriptors
    whereas FileIO (stdin, stdout, stderr) do'''
    def fileno(self):
        return 0

    def write(self, input_buffer):
        sys.__stdout__.write(input_buffer)
        for line in input_buffer.rstrip().splitlines():
            self.output_logger.log(
                self.note_level,
                line,
            )

    def readline(self, length=None):
        output_buffer = sys.__stdin__.readline(-1)
        for line in output_buffer.rstrip().splitlines():
            self.input_logger.log(
                self.note_level,
                line,
            )
        return output_buffer

    def getvalue(self):
        return self.log_io.getvalue()

    def close(self):
        self.console_io.flush()
        self.console_io.close()

        self.log_io.flush()
        self.console_io.close()

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        sys.stdin = sys.__stdin__

# globals
env.project = "eGazeciarz"
env.user = "egazeciarz"
env.callsign = 'EGT'
env.repo_browser = "https://dev.spistresci.pl/diffusion/%s/" % env.callsign

env.user_path = "/home/%s" % env.user
env.env_path = "%s/venv" % env.user_path
env.repo_path = "%(path)s/%(project)s" % {
    "path": env.user_path,
    "project": env.project,
}

env.prompt = True
env.logger = None

env_vars = {
    'test': {
        'subdomain': 'test',
        'branch': 'dev',
        'port': 1337,
        'log_compherence': 24,
    },
    'staging': {
        'subdomain': 'staging',
        'branch': 'dev',
        'port': 1337,
        'log_compherence': 25,
    },
    'production': {
        'subdomain': 'beta',
        'branch': 'master',
        'port': 1337,
        'log_compherence': 26,
    },
}


def _set_vars(environment):
    env.environment = environment
    subdomain = env_vars[environment]['subdomain']
    port = env_vars[environment]['port']

    env.hosts = [
        "%s@%s.egazeciarz.pl:%d" % (
            env.user,
            subdomain,
            port,
        )
    ]
    env.branch = env_vars[environment]['branch']
    env.repo_path += "_%s" % env.environment
    env.work_path = "%s/egazeciarz" % env.repo_path
    env.env_path += "_%s" % env.environment
    env.log_compherence = env_vars[environment]['log_compherence']


@task
def production():
    """
    Select production environment
    """
    _set_vars('production')


@task
def staging():
    """
    Select staging environment
    """
    _set_vars('staging')


@task
def test():
    """
    Select test environment
    """
    _set_vars('test')


@task
def noinput():
    """
    Answer affirmatively to all prompts
    """
    env.prompt = False


def pull_changes():
    """
    Switch to appropriate branch and pull changes from upstream
    """

    check_prompt = (
        not env.prompt or
        console.confirm(
            "Switch to appropriate branch and pull changes from upstream?",
            default=True,
        )
    )

    if check_prompt:
        with cd(env.repo_path):
            run("git checkout %s" % env.branch)
            run("git pull")


def update_requirements():
    """
    Update virtualenv requirements based on requirements.txt file
    """

    check_prompt = (
        not env.prompt or
        console.confirm(
            "Update virtualenv requirements based on requirements.txt file?",
            default=True,
        )
    )

    if check_prompt:
        with cd("%s" % env.repo_path):
            with prefix("source %s/bin/activate" % env.env_path):
                run(
                    "pip install"
                    " --requirement %s/requirements.txt" % env.repo_path
                )


def collect_static():
    """
    Collect static files and copy them to collect_static
    """

    check_promt = (
        not env.prompt or
        console.confirm(
            "Collect static files and copy them to collect_static?",
            default=True,
        )
    )

    if check_promt:
        with cd("%s" % env.work_path):
            with prefix("source %s/bin/activate" % env.env_path):
                run(
                    "./manage.py collectstatic"
                    " --noinput"
                )


def sync_db():
    """
    Create tables for models which have not yet been installed
    """

    check_prompt = (
        not env.prompt or
        console.confirm(
            "Create tables for models which have not yet been installed?",
            default=True,
        )
    )

    if check_prompt:
        with cd("%s" % env.work_path):
            with prefix("source %s/bin/activate" % env.env_path):
                run(
                    "./manage.py syncdb"
                    " --noinput"
                )


def cleanup_pyc():
    """
    Remove .pyc files
    """
    check_prompt = (
        not env.prompt
        or console.confirm(
            "Remove .pyc files?",
            default=True,
        )
    )

    if check_prompt:
        with cd("%s" % env.repo_path):
            run("find . -name \*.pyc -delete")


def restart_apache():
    """
    Restart Apache web server
    """
    check_prompt = (
        not env.prompt or
        console.confirm(
            "Restart Apache web server?",
            default=True,
        )
    )

    if check_prompt:
        sudo("service apache2 restart")


@task
def deploy():
    """
    Deploy code to remote host
    """
    require(
        "environment",
        provided_by=[
            production,
            staging,
            test,
        ]
    )

    env.logger = IOLogger('DEBUG')

    check_prompt = (
        env.prompt and
        env.environment == "production" and
        not console.confirm(
            "Are you sure you want to deploy production?",
            default=False,
        )
    )
    if check_prompt:
        abort("Production deployment aborted.")

    pull_changes()
    update_requirements()
    collect_static()
    sync_db()
    cleanup_pyc()
    restart_apache()


@task(default=True)
def usage():
    """
    Print usage examples
    """

    print(dedent(
        """
        Usage examples:
        Test deployment:
            $ fab [noinput] test deploy
        Staging deployment:
            $ fab [noinput] staging deploy
        Production deployment:
            $ fab [noinput] production deploy
        """
    ))


@register
def publish_log():

    if not env.logger:
        return

    log_output = env.logger.getvalue()
    env.logger.close()

    phabricator = Phabricator()
    phabricator.update_interfaces()
    deployer = phabricator.user.whoami()


    info_dict = {
        "arguments": " ".join(sys.argv[1:]),
        "user": deployer.userName,
        "date": datetime.now().strftime('%Y-%m-%d %H:%M'),
    }

    paste_title = "fab %(arguments)s # %(user)s at %(date)s" % info_dict

    paste = phabricator.paste.create(
        content=log_output,
        title=paste_title,
    )

    info_dict.update({
        "paste_id": paste.id,
        "branch": env.branch,
        "branch_repo_url": "%(repo_browser_url)shistory/%(branch)s/" % {
            "repo_browser_url": env.repo_browser,
            "branch": env.branch,
        }
    })

    msg = "P%(paste_id)d `fab %(arguments)s` # @%(user)s at %(date)s " \
          "from branch [%(branch)s](%(branch_repo_url)s) " % info_dict

    phabricator.conpherence.updatethread(
        id=env.log_compherence,
        message=msg,
    )
