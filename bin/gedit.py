#!/usr/bin/env python3
"""
Wrapper for 'gedit' command
"""

import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


class Options:

    def __init__(self, args):
        self._gedit = syslib.Command('gedit')
        self._gedit.setArgs(args[1:])
        self._filter = ('^$|$HOME/.gnome|FAMOpen| DEBUG: |GEDIT_IS_PLUGIN|IPP request failed|'
                        'egg_recent_model_|g_bookmark_file_get_size:|recently-used.xbel|'
                        'Could not load theme')

    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def getGedit(self):
        """
        Return gedit Command class object.
        """
        return self._gedit


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getGedit().run(filter=options.getFilter(), mode='background')
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
