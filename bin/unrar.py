#!/usr/bin/env python3
"""
Unpack a compressed archive in RAR format.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_archiver(self):
        """
        Return archiver Command class object.
        """
        return self._archiver

    def get_archives(self):
        """
        Return list of archives files.
        """
        return self._args.archives

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Unpack a compressed archive in RAR format.')

        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='Show contents of archive.')
        parser.add_argument('-test', dest='testFlag', action='store_true',
                            help='Test archive data only.')

        parser.add_argument('archives', nargs='+', metavar='file.rar',
                            help='Archive file.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._archiver = syslib.Command('unrar')
        if args[1] in ('l', 't', 'x'):
            self._archiver.set_args(args[1:])
            self._archiver.run(mode='exec')

        if self._args.viewFlag:
            self._archiver.set_flags(['l', '-std'])
        elif self._args.testFlag:
            self._archiver.set_flags(['t', '-std'])
        else:
            self._archiver.set_flags(['x', '-std'])


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

        os.umask(int('022', 8))
        archiver = options.get_archiver()

        for archive in options.get_archives():
            archiver.set_args([archive])
            archiver.run()
            if archiver.get_exitcode():
                print(sys.argv[0] + ': Error code ' + str(archiver.get_exitcode()) +
                      ' received from "' + archiver.get_file() + '".', file=sys.stderr)
                raise SystemExit(archiver.get_exitcode())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
