#!/usr/bin/env python3
"""
Wrapper for 'thunderbird' command
"""

import glob
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
        self._thunderbird = syslib.Command('thunderbird')
        if len(args) > 1:
            self._thunderbird.set_args(args[1:])
            if args[1] in ('-v', '-version', '--version'):
                self._thunderbird.run(mode='exec')

        self._filter = '^added$|profile-after-change|mail-startup-done'

        self._config()

    def get_filter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def get_thunderbird(self):
        """
        Return thunderbird Command class object.
        """
        return self._thunderbird

    def _config(self):
        if 'HOME' in os.environ:
            thunderbirddir = os.path.join(os.environ['HOME'], '.thunderbird')
            if os.path.isdir(thunderbirddir):
                os.chmod(thunderbirddir, int('700', 8))


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
            options.get_thunderbird().run(filter=options.get_filter(), mode='background')
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
