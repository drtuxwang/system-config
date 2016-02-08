#!/usr/bin/env python3
"""
Unpack a compressed archive in TAR.LZMA format.
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

    def get_archives(self):
        """
        Return list of archives.
        """
        return self._args.archives

    def get_view_flag(self):
        """
        Return view flag.
        """
        return self._args.viewFlag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Unpack a compressed archive in TAR.LZMA format.')

        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='Show contents of archive.')

        parser.add_argument('archives', nargs='+', metavar='file.tar.lzma|file.tlz',
                            help='Archive file.')

        self._args = parser.parse_args(args)

        for archive in self._args.archives:
            if not archive.endswith('.tar.lzma') and not archive.endswith('.tlz'):
                raise SystemExit(sys.argv[0] + ': Unsupported "' + archive + '" archive format.')

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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
        tar = syslib.Command('tar')
        for archive in options.get_archives():
            print(archive + ':')
            if options.get_view_flag():
                tar.set_args(['tfv', archive])
            else:
                tar.set_args(['xfv', archive])
            tar.run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
