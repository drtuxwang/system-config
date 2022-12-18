#!/usr/bin/env python3
"""
Play system bell sound
"""

import glob
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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        if sys.argv[0].endswith('.py'):
            sound = f'{sys.argv[0][:-3]}.ogg'
        else:
            sound = f'{sys.argv[0]}.ogg'

        if not Path(sound).is_file():
            raise SystemExit(f'{sys.argv[0]}: Cannot find "{sound}" file.')
        bell = command_mod.Command('vlc', args=[
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
            bell = command_mod.Command('ogg123', errors='ignore')
            if not bell.is_found():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find required '
                    '"vlc" or "ogg123" software.',
                )
        bell.append_arg(sound)

        subtask_mod.Batch(bell.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
