#!/usr/bin/env python3
"""
Unpack a compressed archive in RPM format.
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
        self._parseArgs(args[1:])

        self._rpm2cpio = syslib.Command('rpm2cpio')
        self._cpio = syslib.Command('cpio')
        if self._args.viewFlag:
            self._cpio.setArgs(['-idmt', '--no-absolute-filenames'])
        else:
            self._cpio.setArgs(['-idmv', '--no-absolute-filenames'])

    def getArchives(self):
        """
        Return list of archive files.
        """
        return self._args.archives

    def getCpio(self):
        """
        Return cpio Command class object.
        """
        return self._cpio

    def getRpm2cpio(self):
        """
        Return rpm2cpio Command class object.
        """
        return self._rpm2cpio

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Unpack a compressed archive in RPM format.')

        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='Show contents of archive.')

        parser.add_argument('archives', nargs='+', metavar='file.rpm',
                            help='Archive file.')

        self._args = parser.parse_args(args)


class Unpack:

    def __init__(self, options):
        os.umask(int('022', 8))
        cpio = options.getCpio()
        rpm2cpio = options.getRpm2cpio()

        for archive in options.getArchives():
            if not os.path.isfile(archive):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + archive + '" archive file.')
            print(archive + ':')
            rpm2cpio.setArgs([archive])
            rpm2cpio.run(pipes=[cpio])
            if rpm2cpio.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(rpm2cpio.getExitcode()) +
                                 ' received from "' + rpm2cpio.getFile() + '".')


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
