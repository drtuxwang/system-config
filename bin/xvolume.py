#!/usr/bin/env python3
"""
Desktop audio volume utility.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        self._pacmd = syslib.Command('pacmd')

        change = self._args.change
        if change == '+':
            volume = min(self._getvol() + 1, 16)
        elif change == '-':
            volume = max(self._getvol() - 1, 0)
        elif change == '=':
            volume = 10
        else:
            volume = self._getvol()
        self._pacmd.set_args(['set-sink-volume', '0', '0x{0:X}'.format(volume * 0x1000)])

    def get_pacmd(self):
        """
        Return pacmd Command class object.
        """
        return self._pacmd

    def _getvol(self):
        self._pacmd.set_args(['dump'])
        self._pacmd.run(filter='^set-sink-volume', mode='batch')
        try:
            # From 0 - 15
            return int(int(self._pacmd.get_output()[0].split()[2], 16) / 0x1000)
        except (IndexError, ValueError):
            raise SystemExit(sys.argv[0] + ': Cannot detect current Pulseaudio volume.')

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Desktop audio volume utility.')

        parser.add_argument('-dec', action='store_const', const='-', dest='change',
                            help='Increase brightness.')
        parser.add_argument('-inc', action='store_const', const='+', dest='change',
                            help='Default brightness.')
        parser.add_argument('-reset', action='store_const', const='=', dest='change',
                            help='Decrease brightness.')

        self._args = parser.parse_args(args)


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
            options.get_pacmd().run(mode='exec')
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
