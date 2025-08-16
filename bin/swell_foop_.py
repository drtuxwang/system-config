#!/usr/bin/env python3
"""
Sandbox for "swell-foop" command
"""

import os
import signal
import sys
from pathlib import Path

from network_mod import Sandbox
from subtask_mod import Background


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
        command = Sandbox(
            '/usr/games/swell-foop',
            args=sys.argv[1:],
            errors='stop'
        )

        # Start slow for very large history (.local/share/swell-foop/)
        if not Path(f'{command.get_file()}.py').is_file():
            configs = [
                '/dev/dri',
                f'/run/user/{os.getuid()}/dconf',
                Path(Path.home(), '.config/dconf'),
            ]
            command.sandbox(configs)

        Background(command.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
