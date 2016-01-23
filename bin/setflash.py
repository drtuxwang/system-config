#!/usr/bin/env python3
"""
Locate newest Pepper Flash library.
"""

import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.0, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._flash = syslib.Command('libpepflashplayer.so', check=False)
        if not self._flash.is_found():
            setflash = syslib.Command('setflash', check=False)
            if setflash.is_found():
                setflash.run(mode='exec')

    def get_library(self):
        """
        Return library file.
        """
        return self._flash.get_file()


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        try:
            options = Options()
            print(options.get_library())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
