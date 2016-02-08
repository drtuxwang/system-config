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

    def _config(self):
        for file in glob.glob('.~lock.*#'):  # Remove stupid lock files
            try:
                os.remove(file)
            except OSError:
                pass

        offline = syslib.Command("offline", check=False)
        if offline.is_found():
            self._soffice.set_wrapper(offline)
            self._pattern += "|: GConf-WARNING|: Connection refused|GConf warning: |GConf Error: "

    @staticmethod
    def _setenv():
        if 'GTK_MODULES' in os.environ:
            del os.environ['GTK_MODULES']  # Fix Linux 'gnomebreakpad' problems

    def run(self):
        """
        Start program
        """
        self._soffice = syslib.Command(os.path.join('program', 'soffice'))
        self._soffice.set_args(sys.argv[1:])
        if sys.argv[1:] == ['--version']:
            self._soffice.run(mode='exec')
        self._pattern = ('^$|: GLib-CRITICAL |: GLib-GObject-WARNING |: Gtk-WARNING |'
                         ': wrong ELF class:|: Could not find a Java Runtime|'
                         ': failed to read path from javaldx|^Failed to load module:|'
                         'unary operator expected|: unable to get gail version number|gtk printer')
        self._config()
        self._setenv()

        self._soffice.run(filter=self._pattern, mode='background')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
