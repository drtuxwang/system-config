#!/usr/bin/env python3
"""
Print the strings of printable characters in files.
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
            description='Print the strings of printable characters in files.')

        parser.add_argument('files', nargs='+', metavar='file', help='File to search.')

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

    def _file(self, file):
        try:
            with open(file, 'rb') as ifile:
                self._pipe(ifile)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')

    @staticmethod
    def _pipe(pipe):
        string = ''
        while True:
            data = pipe.read(4096)
            if len(data) == 0:
                break
            for byte in data:
                if byte > 31 and byte < 127:
                    string += chr(byte)
                else:
                    if len(string) >= 4:
                        print(string)
                    string = ''
        if string:
            print(string)

    def run(self):
        """
        Start program
        """
        options = Options()

        if len(options.get_files()) == 0:
            self._pipe(sys.stdin.buffer)
        else:
            for file in options.get_files():
                self._file(file)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
