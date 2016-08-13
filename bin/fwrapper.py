#!/usr/bin/env python3
"""
Create wrapper to run script/executable.
"""

import argparse
import glob
import os
import signal
import sys

import file_mod

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
            description='Create wrapper to run script/executable.')

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='Script/executable to wrap.'
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
    def _create(file, link):
        try:
            with open(link, 'w', newline='\n') as ofile:
                print('#!/bin/bash', file=ofile)
                print('#', file=ofile)
                print('# fwrapper.py generated script', file=ofile)
                print('#\n', file=ofile)
                print('MYDIR=$(dirname "$0")', file=ofile)
                if file == os.path.abspath(file):
                    directory = os.path.dirname(file)
                    print(
                        'PATH=$(echo "$PATH" | sed -e "s@$MYDIR@' +
                        directory + '@")',
                        file=ofile
                    )
                    print('export PATH\n', file=ofile)
                    print('exec "' + file + '" "$@"', file=ofile)
                else:
                    print('exec "$MYDIR/' + file + '" "$@"', file=ofile)

            os.chmod(link, int('755', 8))
            file_time = file_mod.FileStat(file).get_time()
            os.utime(link, (file_time, file_time))
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + link + '" wrapper file.')

    def run(self):
        """
        Start program
        """
        options = Options()

        self._files = options.get_files()
        for file in self._files:
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" file.')

            link = os.path.basename(file)
            if os.path.exists(link):
                print('Updating "{0:s}" wrapper for "{1:s}"...'.format(
                    link, file))
            else:
                print('Creating "{0:s}" wrapper for "{1:s}"...'.format(
                    link, file))
            self._create(file, link)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
