#!/usr/bin/env python3
"""
Wrapper for "kubectl" command
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

    @staticmethod
    def _cache() -> None:
        kube_directory = Path(Path.home(), '.kube')
        if not kube_directory.is_dir():
            try:
                os.mkdir(kube_directory)
            except OSError:
                return

        for cache in ('cache', 'http-cache'):
            link = Path(kube_directory, cache)
            directory = FileUtil.tmpdir(Path('.cache', 'kube', cache))
            if not link.is_symlink():
                try:
                    if link.exists():
                        shutil.rmtree(link)
                    link.symlink_to(directory)
                except OSError:
                    pass

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        cls._cache()

        kubectl = Command('kubectl', errors='stop')
        kubectl.set_args(sys.argv[1:])
        Exec(kubectl.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
