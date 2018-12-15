#!/usr/bin/env python3
"""
Wrapper for "evince" command
"""

import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Main:
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

    @staticmethod
    def _config():
        home = os.environ.get('HOME', '')
        file = os.path.join(home, '.gnome2', 'evince', 'print-settings')
        if os.path.isfile(file):
            try:
                os.remove(file)
            except OSError:
                pass

    @staticmethod
    def _setenv():
        # Default to A4
        os.environ['LC_PAPER'] = os.environ.get('LC_PAPER', 'en_GB.UTF-8')

        if 'PRINTER' not in os.environ:
            lpstat = command_mod.Command(
                'lpstat',
                args=['-d'],
                errors='ignore'
            )
            if lpstat.is_found():
                task = subtask_mod.Background(lpstat.get_cmdline())
                task.run(pattern='^system default destination: ')
                if task.has_output():
                    os.environ['PRINTER'] = task.get_output()[0].split()[-1]

    def run(self):
        """
        Start program
        """
        evince = command_mod.Command(
            'evince',
            args=sys.argv[1:],
            errors='stop'
        )
        pattern = (
            '^$|: Gtk-WARNING | Gtk-CRITICAL | GLib-CRITICAL |'
            ' Poppler-WARNING |: Failed to create dbus proxy|:'
            ' invalid matrix |: Page transition|ToUnicode CMap|'
            ': Illegal character|^undefined|'
            ': Page additional action object.*is wrong type|'
            ' Unimplemented annotation:|: No current point in closepath|:'
            ' Invalid Font Weight|: invalid value|accessibility bus address:'
        )
        self._config()
        self._setenv()

        task = subtask_mod.Task(evince.get_cmdline())
        task.run(pattern=pattern)
        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
