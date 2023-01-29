#!/usr/bin/env python3
"""
Wrapper for "engrampa/file-roller" command
"""

import os
import signal
import sys
from pathlib import Path

import command_mod
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
        command = command_mod.Command(
            'engrampa',
            args=sys.argv[1:],
            errors='ignore'
        )
        if not command.is_found():
            command = command_mod.Command(
                'file-roller',
                args=sys.argv[1:],
                errors='stop'
            )

        pattern = '^$|dbind-WARNING|Gtk-WARNING'
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
