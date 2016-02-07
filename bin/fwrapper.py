#!/usr/bin/env python3
"""
Create wrapper to run script/executable.
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
        parser = argparse.ArgumentParser(description='Create wrapper to run script/executable.')

        parser.add_argument('files', nargs='+', metavar='file', help='Script/executable to wrap.')

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
    def _create(source, target):
        try:
            with open(target, 'w', newline='\n') as ofile:
                print('#!/bin/sh', file=ofile)
                print('# fwrapper generated script', file=ofile)
                print('PATH=`echo "$PATH" | sed -e "s@\\`dirname \\"$0\\"\\`@' +
                      os.path.dirname(source) + '@"` export PATH', file=ofile)
                print('exec "' + source + '" "$@"', file=ofile)
            os.chmod(target, int('755', 8))
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot create "' + target + '" wrapper file.')

    def run(self):
        """
        Start program
        """
        options = Options()

        self._files = options.get_files()
        for file in self._files:
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" file.')
            source = os.path.abspath(file)

            target = os.path.basename(file)
            if os.path.exists(target):
                print('Skipping "', target, '" wrapper for "', source, '"...', sep='')
            else:
                print('Creating "', target, '" wrapper for "', source, '"...', sep='')
                self._create(source, target)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
