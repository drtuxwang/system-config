#!/usr/bin/env python3
"""
MyQS, My Queuing System wrapper for legacy qsub, qdel and qstat
"""

import os
import signal
import socket
import sys
from pathlib import Path

from command_mod import Command
from subtask_mod import Exec
from task_mod import Tasks


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

    def _has_myqsd(self) -> bool:
        path = Path(self._myqsdir, 'myqsd.pid')
        try:
            with path.open(errors='replace') as ifile:
                try:
                    pid = int(ifile.readline().strip())
                except (OSError, ValueError):
                    pass
                else:
                    if Tasks.factory().haspid(pid):
                        return True
                    path.unlink()
        except OSError:
            pass
        return False

    def run(self) -> int:
        """
        Start program
        """
        self._myqsdir = Path(
            Path.home(),
            '.config',
            'myqs',
            socket.gethostname().split('.')[0].lower()
        )

        name = Path(sys.argv[0]).stem
        if not self._has_myqsd():
            command = Command(name, errors='ignore')
            if command.is_found():
                Exec(command.get_cmdline() + sys.argv[1:]).run()
        command = Command(f'my{name}', errors='stop')
        Exec(command.get_cmdline() + sys.argv[1:]).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
