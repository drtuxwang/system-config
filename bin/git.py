#!/usr/bin/env python3
"""
Wrapper for GIT revision control system
"""

import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


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

    def get_git(self):
        """
        Return git Command class object.
        """
        return self._git

    @staticmethod
    def _config():
        if 'HOME' in os.environ:
            file = os.path.join(os.environ['HOME'], '.gitconfig')
            if not os.path.isfile(file):
                try:
                    with open(file, 'w', newline='\n') as ofile:
                        user = syslib.info.get_username()
                        host = syslib.info.get_hostname()
                        print('[user]', file=ofile)
                        print('        name =', user, file=ofile)
                        print('        email =', user + '@' + host, file=ofile)
                except OSError:
                    pass

    def parse(self, args):
        """
        Parse arguments
        """
        self._git = syslib.Command(os.path.join('bin', 'git'))
        self._git.set_args(args[1:])

        self._env = {}
        git_home = os.path.dirname(os.path.dirname(self._git.get_file()))
        if git_home not in ('/usr', '/usr/local', '/opt/software'):
            self._env['GIT_EXEC_PATH'] = os.path.join(git_home, 'libexec', 'git-core')
            self._env['GIT_TEMPLATE_DIR'] = os.path.join(git_home, 'share', 'git-core', 'templates')

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

        options.get_git().run(mode='exec', env=options.get_env())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
