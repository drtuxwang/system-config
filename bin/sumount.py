#!/usr/bin/env python3
"""
Unmount file system securely mounted with SSH protocol.
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


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._directories = []
        for directory in args[1:]:
            self._directories.append(os.path.abspath(directory))

    def getDirectorys(self):
        """
        Return list of directories.
        """
        return self._args.directories

        print('\nsumount - Securely unmount a file system using ssh protocol\n')
        print('Usage: sumount /localpath1 [/locapath2 [...]]')

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Unmount file system securely mounted with SSH protocol.')

        parser.add_argument('directories', nargs='+', metavar='localpath',
                            help='Local directory.')
        self._args = parser.parse_args(args)


class Unmount(syslib.Dump):

    def __init__(self, options):
        self._directories = options.getDirectorys()
        self._mount = syslib.Command('mount')
        self._fusermount = syslib.Command('fusermount')

    def run(self):
        for directory in self._directories:
            self._mount.run(filter=' ' + directory + ' type fuse.sshfs ', mode='batch')
            if not self._mount.hasOutput():
                raise SystemExit(sys.argv[0] + ': "' + directory + '" is not a mount point.')
            elif self._mount.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(self._mount.getExitcode()) +
                                 ' received from "' + self._mount.getFile() + '".')
            self._fusermount.setArgs(['-u', directory])
            self._fusermount.run()


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Unmount(options).run()
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
