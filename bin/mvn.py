#!/usr/bin/env python3
"""
MAVEN launcher
"""

import os
import shutil
import signal
import sys
from pathlib import Path

from command_mod import Command
from file_mod import FileUtil
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

        # Send ".m2" to tmpfs
        tmpdir_path = Path(FileUtil.tmpdir(Path('.cache', 'm2')))
        path = Path(Path.home(), '.m2')
        if not path.is_symlink():
            try:
                shutil.rmtree(path)
            except OSError:
                pass
            try:
                tmpdir_path.symlink_to(path)
            except OSError:
                pass

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        mvn = Command('bin/mvn', args=sys.argv[1:], errors='stop')

        Exec(mvn.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
