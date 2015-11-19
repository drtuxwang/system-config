#!/usr/bin/env python3
"""
Compress a file in BZIP2 format.
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

        self._bzip2 = syslib.Command('bzip2')
        self._bzip2.setFlags(['-9'])
        self._bzip2.setArgs(self._args.files)

    def getBzip2(self):
        """
        Return bzip2 Command class object.
        """
        return self._bzip2

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Compress a file in BZIP2 format.')

        parser.add_argument('files', nargs=1, metavar='file',
                            help='File to compresss to "file.bz2".')

        self._args = parser.parse_args(args)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getBzip2().run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.getBzip2().getExitcode())

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
