#!/usr/bin/env python3
"""
Wrapper for "wine" command

Use "-reset" to clean ".wine" junk
"""

import os
import signal
import shutil
import sys
import types
from pathlib import Path
from typing import Any, Callable, Union

from subtask_mod import Batch, Task
from command_mod import Command


class Options:
    """
    Options class
    """
    _wine = Command(Path(sys.argv[0]).name, errors='stop')

    def __init__(self) -> None:
        self._args = None
        self._config()
        self.parse(sys.argv)

    def get_wine(self) -> Command:
        """
        Return wine Command class object.
        """
        return self._wine

    @staticmethod
    def _reset() -> None:
        path = Path(Path.home(), '.wine')
        if path.is_dir():
            print(f'Removing "{path}"...')
            try:
                shutil.rmtree(path)
            except OSError:
                pass

    @staticmethod
    def _signal_ignore(
        # pylint: disable=no-member
        _signal: int,
        _frame: types.FrameType,
    ) -> Union[
        Callable[[signal.Signals, types.FrameType], Any],
        int,
        signal.Handlers,
        None,
    ]:
        pass

    @classmethod
    def _config(cls) -> None:
        signal.signal(signal.SIGINT, cls._signal_ignore)
        signal.signal(signal.SIGTERM, cls._signal_ignore)
#        os.environ['WINEDLLOVERRIDES'] = os.environ.get(
#            'WINEDLLOVERRIDES',
#            'mscoree,mshtml='
#        )

    def parse(self, args: list) -> None:
        """
        Parse arguments
        """
        if len(args) > 1:
            if args[1].endswith('.bat'):
                self._wine.set_args(['cmd', '/c'])
            elif args[1].endswith('.msi'):
                self._wine.set_args(['cmd', '/c', 'start'])
            elif args[1] == '-reset':
                self._reset()
                raise SystemExit(0)
        self._wine.extend_args(args[1:])


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
    def run() -> int:
        """
        Start program
        """
        options = Options()

        wine = options.get_wine()
        xrandr = Command('xrandr', errors='stop')
        task = Batch(xrandr.get_cmdline())
        task.run(pattern='^  ')
        orig_resolution = 0
        for line in task.get_output():
            if '*' in line:
                break
            orig_resolution += 1

        Task(wine.get_cmdline()).run()

        task = Batch(xrandr.get_cmdline())
        task.run(pattern='^  ')
        new_resolution = 0
        for line in task.get_output():
            if '*' in line:
                break
            new_resolution += 1
        if new_resolution != orig_resolution:
            xrandr.set_args(['-s', orig_resolution])
            Batch(xrandr.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
