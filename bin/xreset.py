#!/usr/bin/env python3
"""
Reset to default screen resolution.

'$HOME/.config/xreset.json' contain configuration information.
"""

import argparse
import glob
import json
import os
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

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

    def get_settings(self):
        """
        Return settings
        """
        return self._config.get()

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Reset to default screen resolution.')

        parser.add_argument('settings', nargs='*', metavar='device=mode',
                            help='Display device (ie "DP1=1920x1080").')

        self._args = parser.parse_args(args)


class Configuration(object):
    """
    Configuration class
    """

    def __init__(self, file=''):
        self._data = {'xreset': {}}
        if file:
            try:
                with open(file) as ifile:
                    self._data = json.load(ifile)
            except (OSError, KeyError, ValueError):
                pass

    def get(self):
        """
        Return device mode
        """
        return self._data['xreset'].items()

    def set(self, device, mode):
        """
        Set device mode
        """
        self._data['xreset'][device] = mode

    def write(self, file):
        """
        Write file
        """
        try:
            with open(file, 'w', newline='\n') as ofile:
                print(json.dumps(self._data, indent=4, sort_keys=True), file=ofile)
        except OSError:
            pass


class Xreset(object):
    """
    Xreset class
    """

    def __init__(self, options):
        self._xrandr = syslib.Command('xrandr')
        self._dpi = '96'
        self._settings = options.get_settings()

    def run(self):
        """
        Run commands
        """
        self._xrandr.set_args(['-s', '0'])
        self._xrandr.run(mode='batch')
        self._xrandr.set_args(['--dpi', self._dpi])
        self._xrandr.run(mode='batch')

        for device, mode in self._settings:
            self._xrandr.set_args(['--output', device, '--auto'])
            self._xrandr.run(mode='batch')
            self._xrandr.set_args(['--output', device, '--mode', mode])
            self._xrandr.run(mode='batch')


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
            Xreset(options).run()
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
