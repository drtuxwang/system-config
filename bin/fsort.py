#!/usr/bin/env python3
"""
Unicode sort lines of a file.
"""

import argparse
import glob
import os
import signal
import sys

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Unicode sort lines of a file.')

        parser.add_argument(
            'files',
            nargs=1,
            metavar='file',
            help='File contents to sort.'
        )

        self._args = parser.parse_args(args)

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

        lines = []
        if len(options.get_files()):
            for file in options.get_files():
                try:
                    with open(file, errors='replace') as ifile:
                        for line in ifile:
                            line = line.rstrip('\r\n')
                            lines.append(line)
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot read "' + file + '" file.')
        else:
            for line in sys.stdin:
                lines.append(line.rstrip('\r\n'))

        for line in sorted(lines):
            print(line)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
