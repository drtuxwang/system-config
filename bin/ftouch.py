#!/usr/bin/env python3
"""
Modify access times of all files in directory recursively.
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


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getDirectories(self):
        """
        Return list of files.
        """
        return self._args.directories

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Modify access times of all files in directory recursively.')

        parser.add_argument('directories', nargs='+', metavar='directory',
                            help='Directory containing files to touch.')

        self._args = parser.parse_args(args)


class Touch(syslib.Dump):

    def __init__(self, options):
        self._touch = syslib.Command('touch', flags=['-a'])
        for directory in options.getDirectories():
            self._toucher(directory)

    def _toucher(self, directory):
        print(directory)
        if os.path.isdir(directory):
            try:
                files = [os.path.join(directory, x) for x in os.listdir(directory)]
                self._touch.setArgs(files)
                self._touch.run(mode='batch')
                for file in files:
                    if os.path.isdir(file) and not os.path.islink(file):
                        self._toucher(file)
            except PermissionError:
                raise SystemExit(sys.argv[0] + ': Cannot open "' + directory + '" directory.')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Touch(options)
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
