#!/usr/bin/env python3
"""
Sandbox for "wesnoth" launcher
"""

import os
import signal
import sys
from pathlib import Path

from network_mod import Sandbox
from subtask_mod import Task


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
    def run() -> None:
        """
        Start program
        """
        name = Path(sys.argv[0]).stem

        wesnoth = Sandbox(name, errors='stop')
        wesnoth.set_args(sys.argv[1:])

        if not Path(f'{wesnoth.get_file()}.py').is_file():
            # Maps $HOME/.config/wesnoth => $HOME/.config
            config_directory = Path(Path.home(), '.config')
            wesnoth_directory = Path(config_directory, 'wesnoth')
            if not wesnoth_directory.is_dir():
                wesnoth_directory.mkdir(parents=True)

            configs = [
                '/dev/dri',
                '/dev/shm',
                f'/run/user/{os.getuid()}/pulse',
                f'{wesnoth_directory}:{config_directory}',
            ]
            if len(sys.argv) >= 2 and sys.argv[1] == '-net':
                wesnoth.set_args(sys.argv[2:])
                configs.append('net')

            # use overlay for portable installation
            path = Path(wesnoth.get_file()).with_name('usr')
            if path.is_dir():
                configs.append(f'{path}:/usr:ol')

            wesnoth.sandbox(configs)

        pattern = 'deprecation:'
        Task(wesnoth.get_cmdline()).run(pattern=pattern)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
