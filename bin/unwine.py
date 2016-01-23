#!/usr/bin/env python3
"""
Shuts down WINE and all Windows applications
"""

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

    def __init__(self):
        self._wineserver = syslib.Command('wineserver', args=['-k'])

    def get_wineserver(self):
        """
        Return wineserver Command class object.
        """
        return self._wineserver


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        try:
            options = Options()
            options.get_wineserver().run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.get_wineserver().get_exitcode())

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
