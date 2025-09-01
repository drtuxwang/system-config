#!/usr/bin/env python3
"""
Sandbox  for "atril/evince" launcher
"""

import glob
import os
import signal
import sys
from pathlib import Path

from command_mod import Command
from network_mod import Sandbox
from subtask_mod import Background, Task


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
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    @staticmethod
    def _config() -> None:
        path = Path(Path.home(), '.gnome2', 'evince', 'print-settings')
        if path.is_file():
            try:
                path.unlink()
            except OSError:
                pass

    @staticmethod
    def _setenv() -> None:
        # Default to A4
        os.environ['LC_PAPER'] = os.environ.get('LC_PAPER', 'en_GB.UTF-8')

        if 'PRINTER' not in os.environ:
            lpstat = Command(
                'lpstat',
                args=['-d'],
                errors='ignore'
            )
            if lpstat.is_found():
                task = Background(lpstat.get_cmdline())
                task.run(pattern='^system default destination: ')
                if task.has_output():
                    os.environ['PRINTER'] = task.get_output()[0].split()[-1]

    def run(self) -> int:
        """
        Start program
        """
        command = Sandbox('atril', errors='ignore')
        if not command.is_found():
            command = Sandbox('evince', args=sys.argv[1:], errors='stop')

        work_path = Path(os.environ['PWD'])
        if work_path == Path.home():
            path = Path(work_path, 'Desktop')
            if path.is_dir():
                os.chdir(path)
                work_path = path

        configs = [
            f'/run/user/{os.getuid()}/dconf',
            Path(Path.home(), '.cache/ibus'),
            Path(Path.home(), '.config/ibus'),
            work_path,
        ] + glob.glob('/tmp/dbus*')

        for arg in sys.argv[1:]:
            path = Path(arg).resolve()
            if arg == '-net':
                configs.append('net')
            elif path.is_dir():
                command.append_arg(path)
                configs.append(path)
            elif path.is_file():
                command.append_arg(path)
                configs.append(path.parent)
            else:
                command.append_arg(arg)

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

        task = Task(command.get_cmdline())
        task.run(pattern=pattern)
        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
