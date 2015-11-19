#!/usr/bin/env python3
"""
Run GUI software and restore resolution.
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

        command = self._args.command[0]
        self._command = syslib.Command(command, pathextra=[command], args=self._commandArgs)

    def getCommand(self):
        """
        Return Command class object.
        """
        return self._command

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Run GUI software and restore resolution.')

        parser.add_argument('command', nargs=1, help='Command to run.')
        parser.add_argument('args', nargs='*', metavar='arg', help='Command argument.')

        self._args = parser.parse_args(args[:1])

        self._commandArgs = args[1:]


class Xrun:

    def __init__(self, options):
        self._command = options.getCommand()

        self._xrandr = syslib.Command('xrandr')
        self._xrandr.run(filter='^  ', mode='batch')
        self._resolution = 0
        for line in self._xrandr.getOutput():
            if '*' in line:
                break
            self._resolution += 1
        self._dpi = '96'

        xrdb = syslib.Command('xrdb', args=['-query'], check=False)
        if xrdb.isFound():
            xrdb.run(mode='batch', filter='^Xft.dpi:\t')
            if xrdb.hasOutput():
                self._dpi = xrdb.getOutput()[0].split()[1]

    def run(self):
        self._command.run()
        self._xrandr.run(filter='^  ', mode='batch')
        resolution = 0

        for line in self._xrandr.getOutput():
            if '*' in line:
                break
            resolution += 1

        if resolution != self._resolution:
            time.sleep(1)
            if self._resolution != 0:
                self._xrandr.setArgs(['-s', '0'])
                self._xrandr.run(mode='batch')
                time.sleep(1)
            self._xrandr.setArgs(['-s', str(self._resolution)])
            self._xrandr.run(mode='batch')

        time.sleep(1)
        self._xrandr.setArgs(['--dpi', self._dpi])
        self._xrandr.run(mode='batch')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Xrun(options).run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.getCommand().getExitcode())

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
