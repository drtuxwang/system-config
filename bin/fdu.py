#!/usr/bin/env python3
"""
Show file disk usage.
"""

import argparse
import glob
import os
import signal
import sys

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


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

    def get_summary_flag(self):
        """
        Return summary flag.
        """
        return self._args.summary_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Show file disk usage.')

        parser.add_argument(
            '-s',
            dest='summary_flag',
            action='store_true',
            help='Show summary only.'
        )
        parser.add_argument(
            'files',
            nargs='*',
            default=[os.curdir],
            metavar='file',
            help='File or directory.'
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

    def _usage(self, options, directory):
        size = 0
        try:
            files = [os.path.join(directory, x) for x in os.listdir(directory)]
        except PermissionError:
            raise SystemExit(
                sys.argv[0] + ': Cannot open "' + directory + '" directory.')
        for file in sorted(files):
            if not os.path.islink(file):
                if os.path.isdir(file):
                    size += self._usage(options, file)
                else:
                    size += int((os.path.getsize(file) + 1023) / 1024)
        if not options.get_summary_flag():
            print("{0:7d} {1:s}".format(size, directory))
        return size

    def run(self):
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            if os.path.islink(file):
                print("{0:7d} {1:s}".format(0, file))
            else:
                if os.path.isdir(file):
                    size = self._usage(options, file)
                    if options.get_summary_flag():
                        print("{0:7d} {1:s}".format(size, file))
                elif os.path.isfile(file):
                    size = int((os.path.getsize(file) + 1023) / 1024)
                    print("{0:7d} {1:s}".format(size, file))
                else:
                    print("{0:7d} {1:s}".format(0, file))


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
