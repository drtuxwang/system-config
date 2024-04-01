#!/usr/bin/env python3
"""
Concatenate compressed files and print on the standard output.
"""

import gzip
import os
import signal
import sys
from pathlib import Path

from command_mod import Command
from subtask_mod import Exec, Task


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

    def run(self) -> int:
        """
        Start program
        """
        if len(sys.argv) > 1 and sys.argv[1].startswith('-'):
            command = Command('zcat', errors='stop')
            Exec(command.get_cmdline() + sys.argv[1:]).run()

        for path in [Path(x) for x in sys.argv[1:]]:
            if not path.is_file():
                continue

            args = ['-d', '-c', path]
            suffix = path.suffix
            if suffix == '.7z':
                command = Command('7z', errors='stop')
                args = ['x', '-so', path]
            elif suffix in ('.lzma', '.xz'):
                command = Command('xz', errors='stop')
            elif suffix in ('.zst', '.zstd'):
                command = Command('zstd', errors='stop')
            elif suffix == '.bz2':
                command = Command('bzip2', errors='stop')
            elif suffix == '.gz':
                command = Command('gzip', errors='stop')
            else:
                with gzip.open(path, 'r') as ifile:
                    try:
                        ifile.read(1)
                        command = Command('gzip', errors='stop')
                    except OSError:
                        command = Command('fcat', errors='stop')
                        args = [path]

            task = Task(command.get_cmdline() + args)
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
