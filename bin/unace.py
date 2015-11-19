#!/usr/bin/env python3
"""
Unpack a compressed archive in ACE format.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options:

    def __init__(self, args):

        if os.name == 'nt':
            self._archiver = syslib.Command('unace32.exe')
        else:
            self._archiver = syslib.Command('unace')

        if len(args) > 1 and args[1] in ('v', 't', 'x'):
            self._archiver.setArgs(args[1:])
            self._archiver.run(mode='exec')

        self._parseArgs(args[1:])

        if self._args.viewFlag:
            self._archiver.setFlags(['v'])
        elif self._args.testFlag:
            self._archiver.setFlags(['t', '-y'])
        elif os.name == 'nt':
            self._archiver.setFlags(['x', '-y', '-o'])
        else:
            self._archiver.setFlags(['x', '-y', '-o', '-y'])

    def getArchiver(self):
        """
        Return archiver Command class object.
        """
        return self._archiver

    def getArchives(self):
        """
        Return list of archives files.
        """
        return self._args.archives

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Unpack a compressed archive in ACE format.')

        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='Show contents of archive.')
        parser.add_argument('-test', dest='testFlag', action='store_true',
                            help='Test archive data only.')

        parser.add_argument('archives', nargs='+', metavar='file.ace',
                            help='Archive file.')

        self._args = parser.parse_args(args)


class Unpack:

    def __init__(self, options):
        os.umask(int('022', 8))
        archiver = options.getArchiver()

        for archive in options.getArchives():
            archiver.setArgs([archive])
            archiver.run()
            if archiver.getExitcode():
                print(sys.argv[0] + ': Error code ' + str(archiver.getExitcode()) +
                      ' received from "' + archiver.getFile() + '".', file=sys.stderr)
                raise SystemExit(archiver.getExitcode())


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Unpack(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
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
