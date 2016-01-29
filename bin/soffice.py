#!/usr/bin/env python3
"""
LibreOffice launcher
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
        self._soffice = syslib.Command(os.path.join('program', 'soffice'))
        self._soffice.set_args(args[1:])
        if args[1:] == ['--version']:
            self._soffice.run(mode='exec')
        self._filter = ('^$|: GLib-CRITICAL |: GLib-GObject-WARNING |: Gtk-WARNING |'
                        ': wrong ELF class:|: Could not find a Java Runtime|'
                        ': failed to read path from javaldx|^Failed to load module:|'
                        'unary operator expected|: unable to get gail version number|gtk printer')
        self._config()
        self._setenv()

    def get_filter(self):
        """
        Return filter pattern.
        """
        return self._filter

    def get_soffice(self):
        """
        Return soffice Command class object.
        """
        return self._soffice

    def _config(self):
        for file in glob.glob('.~lock.*#'):  # Remove stupid lock files
            try:
                os.remove(file)
            except OSError:
                pass

        offline = syslib.Command("offline", check=False)
        if offline.is_found():
            self._soffice.set_wrapper(offline)
            self._filter += "|: GConf-WARNING|: Connection refused|GConf warning: |GConf Error: "

    def _setenv(self):
        if 'GTK_MODULES' in os.environ:
            del os.environ['GTK_MODULES']  # Fix Linux 'gnomebreakpad' problems


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
            options.get_soffice().run(filter=options.get_filter(), mode='background')
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
