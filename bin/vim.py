#!/usr/bin/env python3
"""
Wrapper for "vim" command
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
    def run() -> int:
        """
        Start program
        """
        if Path('/usr/bin/vim').is_file():
            command = command_mod.Command('vim', errors='stop')
            if '-n' not in sys.argv[1:]:
                command.set_args(['-N', '-n', '-i', 'NONE', '-T', 'xterm'])
        else:
            command = command_mod.Command('vi', errors='stop')
        command.extend_args([os.path.expandvars(x) for x in sys.argv[1:]])

        task = subtask_mod.Task(command.get_cmdline())
        task.run()
        if task.get_exitcode():
            print(
                f'{sys.argv[0]}: Error code '
                f'{task.get_exitcode()} received from "{task.get_file()}".',
                file=sys.stderr,
            )
            raise SystemExit(task.get_exitcode())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
