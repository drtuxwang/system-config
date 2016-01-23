#!/usr/bin/env python3
"""
Play system bell sound
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
        if args[0].endswith('.py'):
            sound = args[0][:-3] + '.ogg'
        else:
            sound = args[0] + '.ogg'

        if not os.path.isfile(sound):
            raise SystemExit(sys.argv[0] + ': Cannot find "' + sound + '" file.')
        self._bell = syslib.Command('ogg123', check=False)
        if not self._bell.is_found():
            self._bell = syslib.Command('cvlc', flags=['--play-and-exit'], check=False)
            if not self._bell.is_found():
                raise SystemExit(sys.argv[0] + ': Cannot find required "ogg123" or'
                                 ' "cvlc" software.')
        self._bell.set_args([sound])

    def get_bell(self):
        """
        Return bell Command class object.
        """
        return self._bell


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
            options.get_bell().run(mode='batch')
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.get_bell().get_exitcode())

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
