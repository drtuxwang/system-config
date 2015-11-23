#!/usr/bin/env python3
"""
Create wrapper to run script/executable.
"""

import argparse
import glob
import os
import signal
import sys

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Create wrapper to run script/executable.')

        parser.add_argument('files', nargs='+', metavar='file', help='Script/executable to wrap.')

        self._args = parser.parse_args(args)


class Wrap:

    def __init__(self, options):
        self._files = options.getFiles()

    def _create(self, source, target):
        try:
            with open(target, 'w', newline='\n') as ofile:
                print('#!/bin/sh', file=ofile)
                print('# fwrapper generated script', file=ofile)
                print('PATH="' + os.path.dirname(source) + ':$PATH"; export PATH', file=ofile)
                print('exec "' + source + '" "$@"', file=ofile)
            os.chmod(target, int('755', 8))
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot create "' + target + '" wrapper file.')

    def run(self):
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


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Wrap(options).run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windowsArgv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
