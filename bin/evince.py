#!/usr/bin/env python3
"""
Wrapper for 'evince' command
"""

import sys
if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import glob
import os
import signal

import syslib


class Options:

    def __init__(self, args):
        self._evince = syslib.Command('evince')
        self._evince.setArgs(args[1:])
        self._filter = ('^$|: Gtk-WARNING | Gtk-CRITICAL | GLib-CRITICAL | Poppler-WARNING |'
                        ': Failed to create dbus proxy|: invalid matrix |: Page transition|'
                        'ToUnicode CMap|: Illegal character|^undefined|'
                        ': Page additional action object.*is wrong type|'
                        ' Unimplemented annotation:|: No current point in closepath|:'
                        ' Invalid Font Weight|: invalid value')
        self._config()
        self._setenv()

    def getEvince(self):
        """
        Return evince Command class object.
        """
        return self._evince

    def getFilter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def _config(self):
        if 'HOME' in os.environ:
            file = os.path.join(os.environ['HOME'], '.gnome2', 'evince', 'print-settings')
            if os.path.isfile(file):
                try:
                    os.remove(file)
                except OSError:
                    pass

    def _setenv(self):
        if 'LC_PAPER' not in os.environ:  # Default to A4
            os.environ['LC_PAPER'] = 'en_GB.UTF-8'
        if 'PRINTER' not in os.environ:
            lpstat = syslib.Command('lpstat', args=['-d'], check=False)
            if lpstat.isFound():
                lpstat.run(filter='^system default destination: ', mode='batch')
                if lpstat.hasOutput():
                    os.environ['PRINTER'] = lpstat.getOutput()[0].split()[-1]


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getEvince().run(filter=options.getFilter())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.getEvince().getExitcode())

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
