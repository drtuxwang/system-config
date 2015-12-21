#!/usr/bin/env python3
"""
Send popup message to display.
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


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._setpop(self._args.words)

    def getPop(self):
        """
        Return pop Command class object.
        """
        return self._pop

    def getTimeDelay(self):
        """
        Return time delay in minutes.
        """
        return self._args.timeDelay[0]

    def _setpop(self, args):
        self._pop = syslib.Command('notify-send')
        self._pop.setFlags(['--expire-time=0'])
        self._pop.setArgs(args)

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Send popup message to display.')

        parser.add_argument('-time', nargs=1, type=int, dest='timeDelay', default=[0],
                            help='Delay popup in minutes.')

        parser.add_argument('words', nargs='+', metavar='word',
                            help='A word.')

        self._args = parser.parse_args(args)

        if self._args.timeDelay[0] < 0:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for delay time.')


class Message:

    def __init__(self, options):
        self._bell = syslib.Command('bell', check=False)
        self._pop = options.getPop()
        self._delay = 60 * options.getTimeDelay()

    def run(self):
        time.sleep(self._delay)

        if self._bell.isFound():
            self._bell.run(mode='background')

        self._pop.run()
        if self._pop.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(pop.getExitcode()) +
                             ' received from "' + self._pop.getFile() + '".')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Message(options).run()
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
