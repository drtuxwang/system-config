#!/usr/bin/env python3
"""
Watch file system events.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._inotifywait = syslib.Command('inotifywait')
        self._inotifywait.setFlags(['-e', 'create,modify,move,delete', '-mr'])
        self._inotifywait.setArgs(self._args.directories)

    def getInotifywait(self):
        """
        Return inotifywait Command class object.
        """
        return self._inotifywait

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Watch file system events.')

        parser.add_argument('directories', nargs='+', metavar='directory',
                            help='Directory to monitor.')

        self._args = parser.parse_args(args)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getInotifywait().run(mode='exec')
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windowsArgv(self):
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
