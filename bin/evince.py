#!/usr/bin/env python3
"""
Wrapper for 'evince' command
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
        self._evince = syslib.Command('evince')
        self._evince.set_args(args[1:])
        self._filter = ('^$|: Gtk-WARNING | Gtk-CRITICAL | GLib-CRITICAL | Poppler-WARNING |'
                        ': Failed to create dbus proxy|: invalid matrix |: Page transition|'
                        'ToUnicode CMap|: Illegal character|^undefined|'
                        ': Page additional action object.*is wrong type|'
                        ' Unimplemented annotation:|: No current point in closepath|:'
                        ' Invalid Font Weight|: invalid value')
        self._config()
        self._setenv()

    def get_evince(self):
        """
        Return evince Command class object.
        """
        return self._evince

    def get_filter(self):
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
            if lpstat.is_found():
                lpstat.run(filter='^system default destination: ', mode='batch')
                if lpstat.has_output():
                    os.environ['PRINTER'] = lpstat.get_output()[0].split()[-1]


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
            options.get_evince().run(filter=options.get_filter())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(options.get_evince().get_exitcode())

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
