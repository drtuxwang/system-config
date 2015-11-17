#!/usr/bin/env python3
"""
Reset to default screen resolution.

'$HOME/.config/xreset.json' contain configuration information.
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import json
import os
import signal
import time

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

        if 'HOME' not in os.environ:
            raise SystemExit(sys.argv[0] + ': Cannot determine home directory.')

        configdir = os.path.join(os.environ['HOME'], '.config')
        if not os.path.isdir(configdir):
            try:
                os.mkdir(configdir)
            except OSError:
                return
        configfile = os.path.join(configdir, 'xreset.json')
        self._config = Configuration(configfile)

        if self._args.settings:
            for setting in self._args.settings:
                try:
                    device, mode = setting.split('=')
                except ValueError:
                    raise SystemExit(sys.argv[0] + ': Invalid "' + setting + '" settings.')
                self._config.set(device, mode)
            self._config.write(configfile)

    def getSettings(self):
        return self._config.get()

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Reset to default screen resolution.')

        parser.add_argument('settings', nargs='*', metavar='device=mode',
                            help='Display device (ie "DP1=1920x1080").')

        self._args = parser.parse_args(args)


class Configuration(syslib.Dump):

    def __init__(self, file=''):
        self._data = {'xreset': {}}
        if file:
            try:
                with open(file) as ifile:
                    self._data = json.load(ifile)
            except (IOError, KeyError, ValueError):
                pass

    def get(self):
        return self._data['xreset'].items()

    def set(self, device, mode):
        self._data['xreset'][device] = mode

    def write(self, file):
        try:
            with open(file, 'w', newline='\n') as ofile:
                print(json.dumps(self._data, indent=4, sort_keys=True), file=ofile)
        except IOError:
            pass


class Xreset(syslib.Dump):

    def __init__(self, options):
        self._xrandr = syslib.Command('xrandr')
        self._dpi = '96'
        self._settings = options.getSettings()

    def run(self):
        self._xrandr.setArgs(['-s', '0'])
        self._xrandr.run(mode='batch')
        self._xrandr.setArgs(['--dpi', self._dpi])
        self._xrandr.run(mode='batch')

        for device, mode in self._settings:
            self._xrandr.setArgs(['--output', device, '--auto'])
            self._xrandr.run(mode='batch')
            self._xrandr.setArgs(['--output', device, '--mode', mode])
            self._xrandr.run(mode='batch')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Xreset(options).run()
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
