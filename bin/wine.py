#!/usr/bin/env python3
"""
Wrapper for 'wine' command

Use '-reset' to clean '.wine' junk
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal
import shutil

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._wine = syslib.Command('wine')

        if len(args) > 1:
            if args[1].endswith('.bat'):
                self._wine.setFlags(['cmd', '/c'])
            elif args[1].endswith('.msi'):
                self._wine.setFlags(['cmd', '/c', 'start'])
            elif args[1] == '-reset':
                self._reset()
                raise SystemExit(0)
        self._wine.setArgs(args[1:])

        self._signalTrap()
        os.environ['WINEDEBUG'] = '-all'

    def getWine(self):
        """
        Return wine Command class object.
        """
        return self._wine

    def _reset(self):
        if 'HOME' in os.environ:
            directory = os.path.join(os.environ['HOME'], '.wine')
            if os.path.isdir(directory):
                print('Removing "{0:s}"...'.format(directory))
                try:
                    shutil.rmtree(directory)
                except OSError:
                    pass

    def _signalIgnore(self, signal, frame):
        pass

    def _signalTrap(self):
        signal.signal(signal.SIGINT, self._signalIgnore)
        signal.signal(signal.SIGTERM, self._signalIgnore)


class Wine(syslib.Dump):

    def __init__(self, options):
        self._wine = options.getWine()
        self._xrandr = syslib.Command('xrandr')
        self._xrandr.run(filter='^  ', mode='batch')
        self._resolution = 0
        for line in self._xrandr.getOutput():
            if '*' in line:
                break
            self._resolution += 1

    def run(self):
        self._wine.run()
        self._xrandr.run(filter='^  ', mode='batch')
        resolution = 0
        for line in self._xrandr.getOutput():
            if '*' in line:
                break
            resolution += 1
        if resolution != self._resolution:
            self._xrandr.setArgs(['-s', str(self._resolution)])
            self._xrandr.run(mode='batch')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Wine(options).run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.getWine().getExitcode())

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
