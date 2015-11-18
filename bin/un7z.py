#!/usr/bin/env python3
"""
Unpack a compressed archive in 7Z format.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal

import syslib


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._archiver = syslib.Command('7za', check=False)
        if self._archiver.isFound():
            self._archiver = syslib.Command('7z')

        if self._args.viewFlag:
            self._archiver.setFlags(['l'])
        elif self._args.testFlag:
            self._archiver.setFlags(['t'])
        else:
            self._archiver.setFlags(['x', '-y'])

        self._setenv()

    def getArchiver(self):
        """
        Return archiver Command class object.
        """
        return self._archiver

    def getArchives(self):
        """
        Return list of archive files.
        """
        return self._args.archives

    def _setenv(self):
        if 'LANG' in os.environ:
            del os.environ['LANG']  # Avoids locale problems

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Unpack a compressed archive in 7Z format.')

        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='Show contents of archive.')
        parser.add_argument('-test', dest='testFlag', action='store_true',
                            help='Test archive data only.')

        parser.add_argument('archives', nargs='+', metavar='file.7z',
                            help='Archive file.')

        self._args = parser.parse_args(args)


class Unpack:

    def __init__(self, options):
        os.umask(int('022', 8))
        archiver = options.getArchiver()

        if os.name == 'nt':
            for archive in options.getArchives():
                archiver.setArgs([archive])
                archiver.run()
                if archiver.getExitcode():
                    raise SystemExit(sys.argv[0] + ': Error code ' + str(archiver.getExitcode()) +
                                     ' received from "' + archiver.getFile() + '".')
        else:
            for archive in options.getArchives():
                archiver.setArgs([archive])
                archiver.run(replace=('\\', '/'))
                if archiver.getExitcode():
                    raise SystemExit(sys.argv[0] + ': Error code ' + str(archiver.getExitcode()) +
                                     ' received from "' + archiver.getFile() + '".')


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
