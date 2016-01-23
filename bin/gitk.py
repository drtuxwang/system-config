#!/usr/bin/env python3
"""
Wrapper for GITK revision control system
"""

import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._gitk = syslib.Command(os.path.join('bin', 'gitk'))
        self._gitk.set_args(args[1:])

        self._env = {}
        if os.name == 'nt':
            os.environ['PATH'] = os.path.join(os.environ['PATH'],
                                              os.path.dirname(self._gitk.get_file()))
        else:
            git_home = os.path.dirname(os.path.dirname(self._gitk.get_file()))
            if git_home not in ('/usr', '/usr/local', '/opt/software'):
                self._env['GIT_EXEC_PATH'] = os.path.join(git_home, 'libexec', 'git-core')
                self._env['GIT_TEMPLATE_DIR'] = os.path.join(git_home, 'share',
                                                             'git-core', 'templates')

        self._config()

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

    def _config(self):
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


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            options.get_gitk().run(mode='exec', env=options.get_env())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
