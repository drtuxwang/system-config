#!/usr/bin/env python3
"""
Remove horrible characters in filenames.
"""

import argparse
import glob
import re
import os
import shutil
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

    def get_files(self):
        """
        Return list to files.
        """
        return self._files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Remove horrible charcters in filename.')

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='File or directory.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        if len(args) == 1 or args[1] in ('-h', '--h', '--help'):
            self._parse_args(args[1:])

        self._files = args[1:]


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

        is_bad_char = re.compile(r'^-|[ !\'$&`"()*<>?\[\]\\\\|]')
        for file in options.get_files():
            newfile = is_bad_char.sub('_', file)
            if newfile != file:
                if not os.path.isfile(newfile):
                    if not os.path.isdir(newfile):
                        if not os.path.islink(newfile):
                            try:
                                shutil.move(file, newfile)
                            except OSError:
                                pass


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
