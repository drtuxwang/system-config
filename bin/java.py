#!/usr/bin/env python3
"""
JAVA launcher
"""

import os
import shutil
import signal
import sys
from pathlib import Path

from command_mod import Command
from subtask_mod import Exec


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

        # Send ".java" to ".cache/java"
        path = Path(Path.home(), '.cache', 'java')
        if not path.is_dir():
            path.mkdir(parents=True)
        path = Path(Path.home(), '.java')
        if not path.is_symlink():
            if path.is_dir():
                shutil.rmtree(path)
            path.symlink_to(Path('.cache', 'java'))

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        java = Command('bin/java', errors='stop')
        if len(sys.argv) > 1:
            if sys.argv[1].endswith('.jar'):
                java.set_args(['-jar'])
        java.extend_args(sys.argv[1:])

        Exec(java.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
