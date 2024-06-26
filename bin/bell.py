#!/usr/bin/env python3
"""
Play system bell sound
"""

import os
import signal
import sys
from pathlib import Path

from command_mod import Command
from subtask_mod import Batch


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
        sound = (
            f'{sys.argv[0][:-3]}.ogg'
            if sys.argv[0].endswith('.py')
            else f'{sys.argv[0]}.ogg'
        )

        if not Path(sound).is_file():
            raise SystemExit(f'{sys.argv[0]}: Cannot find "{sound}" file.')
        bell = Command('vlc', args=[
            '--intf',
            'dummy',
            '--quiet',
            '--gain',
            '2',
            '--no-repeat',
            '--no-loop',
            '--play-and-exit',
        ], errors='ignore')
        if not bell.is_found():
            bell = Command('ogg123', errors='ignore')
            if not bell.is_found():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find required '
                    '"vlc" or "ogg123" software.',
                )
        bell.append_arg(sound)

        Batch(bell.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
