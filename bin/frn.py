#!/usr/bin/env python3
"""
Rename file/directory by replacing some characters.
"""

import argparse
import glob
import os
import re
import shutil
import signal
import sys

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options:
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

    def get_pattern(self):
        """
        Return regular expression pattern.
        """
        return self._args.pattern[0]

    def get_replacement(self):
        """
        Return replacement.
        """
        return self._args.replacement[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Rename file/directory by replacing some characters.')

        parser.add_argument(
            'pattern',
            nargs=1,
            help='Regular expression.'
        )
        parser.add_argument(
            'replacement',
            nargs=1,
            help='Replacement for matches.'
        )
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
        self._parse_args(args[1:])


class Main:
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

    def run(self):
        """
        Start program
        """
        options = Options()

        try:
            self._is_match = re.compile(options.get_pattern())
        except re.error:
            raise SystemExit(sys.argv[0] + ': Invalid regular expression "' +
                             options.get_pattern() + '".')

        self._replacement = options.get_replacement()
        self._files = options.get_files()

        for file in self._files:
            if os.sep in file:
                newfile = os.path.join(
                    os.path.dirname(file),
                    self._is_match.sub(
                        self._replacement,
                        os.path.basename(file)
                    )
                )
            else:
                newfile = self._is_match.sub(self._replacement, file)
            if newfile != file:
                print('Renaming "' + file + '" to "' + newfile + '"...')
                if os.path.isfile(newfile):
                    raise SystemExit(
                        sys.argv[0] + ': Cannot rename over existing "' +
                        newfile + '" file.'
                    )
                try:
                    shutil.move(file, newfile)
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot rename to "' +
                        newfile + '" file.'
                    )


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
