#!/usr/bin/env python3
"""
Unpack a compressed archive in ZIP format.
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
        self._parse_args(args[1:])

        if os.name == 'nt':
            self._archiver = syslib.Command('pkzip32.exe', check=False)
            if not self._archiver.is_found():
                self._archiver = syslib.Command('unzip')
        else:
            self._archiver = syslib.Command('unzip')

        if args[1] in ('view', 'test'):
            self._archiver.set_args(args[1:])
            self._archiver.run(mode='exec')

        if os.path.basename(self._archiver.get_file()) == 'pkzip32.exe':
            if self._args.viewFlag:
                self._archiver.set_flags(['-view'])
            elif self._args.testFlag:
                self._archiver.set_flags(['-test'])
            else:
                self._archiver.set_flags(['-extract', '-directories'])
        else:
            if self._args.viewFlag:
                self._archiver.set_flags(['-v'])
            elif self._args.testFlag:
                self._archiver.set_flags(['-t'])

    def get_archiver(self):
        """
        Return archiver Command class object.
        """
        return self._archiver

    def get_archives(self):
        """
        Return list of archive files.
        """
        return self._args.archives

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Unpack a compressed archive in ZIP format.')

        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='Show contents of archive.')
        parser.add_argument('-test', dest='testFlag', action='store_true',
                            help='Test archive data only.')

        parser.add_argument('archives', nargs='+', metavar='file.zip',
                            help='Archive file.')

        self._args = parser.parse_args(args)


class Unpack(object):
    """
    Unpack class
    """

    def __init__(self, options):
        os.umask(int('022', 8))
        archiver = options.get_archiver()
        for archive in options.get_archives():
            archiver.set_args([archive])
            archiver.run()
            if archiver.get_exitcode():
                print(sys.argv[0] + ': Error code ' + str(archiver.get_exitcode()) +
                      ' received from "' + archiver.get_file() + '".', file=sys.stderr)
                raise SystemExit(archiver.get_exitcode())


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
            Unpack(options)
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
