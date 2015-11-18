#!/usr/bin/env python3
"""
Make a compressed archive in ZIP format.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal

import syslib


class Options:

    def __init__(self, args):
        if os.name == 'nt':
            self._archiver = syslib.Command('pkzip32.exe', check=False)
            if self._archiver.isFound():
                self._archiver.setFlags(['-add', '-maximum', '-recurse', '-path'])
                self._archiver.setArgs(args[1:])
            else:
                self._archiver = syslib.Command('zip', flags=['-r', '-9'])
        else:
            self._archiver = syslib.Command('zip', flags=['-r', '-9'])

        if len(args) > 1 and args[1] in ('-add', '-r'):
            self._archiver.setArgs(args[1:])
            self._archiver.run(mode='exec')

        self._parseArgs(args[1:])

        if os.path.isdir(self._args.archive[0]):
            self._archiver.setArgs([os.path.abspath(self._args.archive[0] + '.7z')])
        else:
            self._archiver.setArgs(self._args.archive)

        if self._args.files:
            self._archiver.extendArgs(self._args.files)
        else:
            self._archiver.extendArgs(os.listdir())

    def getArchiver(self):
        """
        Return archiver Command class object.
        """
        return self._archiver

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Make a compressed archive in ZIP format.')

        parser.add_argument('archive', nargs=1, metavar='file.zip',
                            help='Archive file or directory.')
        parser.add_argument('files', nargs='*', metavar='file', help='File or directory.')

        self._args = parser.parse_args(args)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getArchiver().run(mode='exec')
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
