#!/usr/bin/env python3
"""
Reset to default screen resolution.

"$HOME/.config/xreset.json" contain configuration information.
"""

import argparse
import glob
import json
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_settings(self):
        """
        Return settings
        """
        return self._config.get()

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Reset to default screen resolution.')

        parser.add_argument(
            'settings',
            nargs='*',
            metavar='device=mode',
            help='Display device (ie "DP1=1920x1080").'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if 'HOME' not in os.environ:
            raise SystemExit(
                sys.argv[0] + ': Cannot determine home directory.')

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
                    raise SystemExit(
                        sys.argv[0] + ': Invalid "' + setting + '" settings.')
                self._config.set(device, mode)
            self._config.write(configfile)


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
                print(
                    json.dumps(self._data, indent=4, sort_keys=True),
                    file=ofile
                )
        except OSError:
            pass


class Main(object):
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def run():
        """
        Start program
        """
        options = Options()

        xrandr = command_mod.Command('xrandr', errors='stop')
        dpi = '96'
        settings = options.get_settings()

        subtask_mod.Batch(xrandr.get_cmdline() + ['-s', '0']).run()
        subtask_mod.Batch(xrandr.get_cmdline() + ['--dpi', dpi]).run()

        for device, mode in settings:
            subtask_mod.Batch(
                xrandr.get_cmdline() + ['--output', device, '--auto']).run()
            subtask_mod.Batch(
                xrandr.get_cmdline() +
                ['--output', device, '--mode', mode]
            ).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
