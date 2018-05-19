#!/usr/bin/env python3
"""
Wrapper for GITK revision control system
"""

import getpass
import glob
import os
import signal
import socket
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_env(self):
        """
        Return dictionary of environments.
        """
        return self._env

    def get_gitk(self):
        """
        Return gitk Command class object.
        """
        return self._gitk

    @staticmethod
    def _config():
        home = os.environ.get('HOME', '')
        file = os.path.join(home, '.gitconfig')
        if not os.path.isfile(file):
            try:
                with open(file, 'w', newline='\n') as ofile:
                    user = getpass.getuser()
                    host = socket.gethostname().split('.')[0].lower()
                    print("[user]", file=ofile)
                    print("        name =", user, file=ofile)
                    print("        email =", user + '@' + host, file=ofile)
            except OSError:
                pass

    def parse(self, args):
        """
        Parse arguments
        """
        self._gitk = command_mod.Command(
            os.path.join('bin', 'gitk'), errors='stop')
        self._gitk.set_args(args[1:])

        self._env = {}
        if os.name == 'nt':
            os.environ['PATH'] = os.path.join(
                os.environ['PATH'], os.path.dirname(self._gitk.get_file()))
        elif not os.path.isfile(self._gitk.get_cmdline()[0] + '.py'):
            git_home = os.path.dirname(os.path.dirname(self._gitk.get_file()))
            if git_home not in ('/usr', '/usr/local', '/opt/software'):
                self._env['GIT_EXEC_PATH'] = os.path.join(
                    git_home, 'libexec', 'git-core')
                self._env['GIT_TEMPLATE_DIR'] = os.path.join(
                    git_home, 'share', 'git-core', 'templates')
        self._config()


class Main(object):
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def run():
        """
        Start program
        """
        options = Options()

        subtask_mod.Exec(
            options.get_gitk().get_cmdline()).run(env=options.get_env())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
