#!/usr/bin/env python3
"""
Make a compressed archive in ZIP format.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        if os.name == 'nt':
            self._archiver = syslib.Command('pkzip32.exe', check=False)
            if self._archiver.is_found():
                self._archiver.set_flags(['-add', '-maximum', '-recurse', '-path'])
                self._archiver.set_args(args[1:])
            else:
                self._archiver = syslib.Command('zip', flags=['-r', '-9'])
        else:
            self._archiver = syslib.Command('zip', flags=['-r', '-9'])

        if len(args) > 1 and args[1] in ('-add', '-r'):
            self._archiver.set_args(args[1:])
            self._archiver.run(mode='exec')

        self._parse_args(args[1:])

        if os.path.isdir(self._args.archive[0]):
            self._archiver.set_args([os.path.abspath(self._args.archive[0] + '.7z')])
        else:
            self._archiver.set_args(self._args.archive)

        if self._args.files:
            self._archiver.extend_args(self._args.files)
        else:
            self._archiver.extend_args(os.listdir())

    def get_archiver(self):
        """
        Return archiver Command class object.
        """
        return self._archiver

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Make a compressed archive in ZIP format.')

        parser.add_argument('archive', nargs=1, metavar='file.zip',
                            help='Archive file or directory.')
        parser.add_argument('files', nargs='*', metavar='file', help='File or directory.')

        self._args = parser.parse_args(args)


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
            options.get_archiver().run(mode='exec')
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
