#!/usr/bin/env python3
"""
Sandbox  for "atril/evince" launcher
"""

import glob
import os
import signal
import sys

import command_mod
import network_mod
import subtask_mod


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config() -> None:
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
    def _config() -> None:
        home = os.environ.get('HOME', '')
        file = os.path.join(home, '.gnome2', 'evince', 'print-settings')
        if os.path.isfile(file):
            try:
                os.remove(file)
            except OSError:
                pass

    @staticmethod
    def _setenv() -> None:
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

    def run(self) -> int:
        """
        Start program
        """
        command = network_mod.Sandbox(
            'atril',
            args=sys.argv[1:],
            errors='ignore'
        )
        if not command.is_found():
            command = network_mod.Sandbox(
                'evince',
                args=sys.argv[1:],
                errors='stop'
            )

        work_dir = os.environ['PWD']
        if work_dir == os.environ['HOME']:
            desktop = os.path.join(work_dir, 'Desktop')
            if os.path.isdir(desktop):
                os.chdir(desktop)
                work_dir = desktop
        configs = [
            f'/run/user/{os.getuid()}/dconf',
            os.path.join(os.getenv('HOME', '/'), '.config/ibus'),
            work_dir,
        ] + glob.glob('/tmp/dbus*')
        if len(sys.argv) > 1:
            configs.append(os.path.dirname(os.path.abspath(sys.argv[1])))
        command.sandbox(configs)

        pattern = (
            '^$|: Gtk-WARNING | Gtk-CRITICAL | GLib-CRITICAL |'
            ' Poppler-WARNING |: Failed to create dbus proxy|'
            ': invalid matrix |: Page transition|ToUnicode CMap|'
            ': Illegal character|^undefined|'
            ': Page additional action object.*is wrong type|'
            ' Unimplemented annotation:|: No current point in closepath|'
            ': Invalid Font Weight|: invalid value|accessibility bus address:|'
            'Error setting file metadata:|no system default destination|'
            'GLib-GObject-WARNING|accessibility bus'
        )
        self._config()
        self._setenv()

        task = subtask_mod.Task(command.get_cmdline())
        task.run(pattern=pattern)
        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
