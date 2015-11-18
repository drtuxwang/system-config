#!/usr/bin/env python3
"""
Fix disk or recovery deleted files.
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

        if self._args.recoverFlag:
            self._photorec()
        else:
            self._testdisk()

        device = self._args.device[0]
        if not os.path.exists(device):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + device + '" disk or disk image file.')
        try:
            with open(self._args.device[0], 'rb') as ifile:
                pass
        except IOError:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + device + '" disk or disk image file.')

        self._command.setArgs([device])

    def getCommand(self):
        """
        Return command Command class object.
        """
        return self._command

    def _photorec(self):
        self._command = syslib.Command('photorec_static', check=False)
        if not self._command.isFound():
            self._command = syslib.Command('testdisk', flags=['-rec'], check=False)
            if not self._command.isFound():
                self._command = syslib.Command('photorec_static')

    def _testdisk(self):
        self._command = syslib.Command('testdisk_static', check=False)
        if not self._command.isFound():
            self._command = syslib.Command('testdisk', check=False)
            if not self._command.isFound():
                self._command = syslib.Command('testdisk_static')

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Fix disk or recovery deleted file.')

        parser.add_argument('-rec', dest='recoverFlag', action='store_true',
                            help='Recover deleted files.')

        parser.add_argument('device', nargs=1, metavar='device|device.img',
                            help='Device or device image (Use "dd").')

        self._args = parser.parse_args(args)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getCommand().run(mode='exec')
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
