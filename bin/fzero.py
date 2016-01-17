#!/usr/bin/env python3
"""
Zero device or create zero file.
"""

import argparse
import glob
import os
import signal
import sys
import time

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

    def get_location(self):
        """
        Return location.
        """
        return self._args.location[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Zero device or create zero file.')

        parser.add_argument('location', nargs=1, metavar='device|directory',
                            help='Device to zero or directory to create "fzero.tmp" file.')

        self._args = parser.parse_args(args)

        location = self._args.location[0]
        if os.path.exists(location):
            if os.path.isfile(location):
                raise SystemExit(sys.argv[0] + ': Cannot zero existing "' + location + '" file.')
        else:
            raise SystemExit(sys.argv[0] + ': Cannot find "' + location + '" device or directory.')


class Zerofile(object):
    """
    Find zero sized file class
    """

    def __init__(self, options):
        if os.path.isdir(options.get_location()):
            file = os.path.join(options.get_location(), 'fzero.tmp')
            print('Creating "' + file + '" zero file...')
        else:
            file = options.get_location()
            print('Zeroing "' + file + '" device...')
        startTime = time.time()
        chunk = 16384 * b'\0'
        size = 0
        try:
            with open(file, 'wb') as ofile:
                while True:
                    for i in range(64):
                        ofile.write(chunk)
                    size += 1
                    sys.stdout.write('\r' + str(size) + ' MB')
                    sys.stdout.flush()
        except (IOError, KeyboardInterrupt):
            pass
        elapsedTime = time.time() - startTime
        print(', {0:4.2f} seconds, {1:.0f} MB/s'.format(elapsedTime, size / elapsedTime))


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            Zerofile(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
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
