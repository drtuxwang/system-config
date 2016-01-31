#!/usr/bin/env python3
"""
Rename window title.
"""

import argparse
import glob
import os
import signal
import sys

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_title(self):
        """
        Return title of files.
        """
        return self._title

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Rename window title.')

        parser.add_argument('words', nargs='+', metavar='word', help='A word.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._title = ' '.join(args[1:])


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

        term = 'Unkown'
        if 'TERM' in os.environ:
            term = os.environ['TERM']

        if term in ['xterm', 'xvt100']:
            sys.stdout.write('\033]0;' + options.get_title() + '\007')
        elif term.startswith('iris-ansi'):
            sys.stdout.write('\033P3.y' + options.get_title() + '\033\\')
            sys.stdout.write('\033P1.y' + options.get_title() + '\033\\')
        else:
            raise SystemExit(sys.argv[0] + ': Unsupported "' + term + '" terminal type.')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
