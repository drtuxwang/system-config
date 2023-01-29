#!/usr/bin/env python3
"""
Wrapper for "xz" command
"""

import os
import signal
import sys
from pathlib import Path

import command_mod
import file_mod
import subtask_mod

VERBOSE_SIZE = 134217728


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
    def _set_libraries(command: command_mod.Command) -> None:
        libdir = Path(Path(command.get_file()).parent, 'lib')
        if libdir.is_dir():
            if os.name != 'nt' and os.uname()[0] == 'Linux':
                if 'LD_LIBRARY_PATH' in os.environ:
                    os.environ['LD_LIBRARY_PATH'] = (
                        f"{libdir}{os.pathsep}{os.environ['LD_LIBRARY_PATH']}"
                    )
                else:
                    os.environ['LD_LIBRARY_PATH'] = str(libdir)

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        command = command_mod.Command('xz', errors='stop')
        if len(sys.argv) > 1 and Path(sys.argv[1]).is_file():
            command.set_args(
                ['-9', '-e', '--x86', '--lzma2=dict=128MiB', '--threads=1'],
            )
            for file in sys.argv[1:]:
                if file_mod.FileStat(file).get_size() > VERBOSE_SIZE:
                    command.append_arg('--verbose')
                    break
        command.extend_args(sys.argv[1:])
        cls._set_libraries(command)

        subtask_mod.Exec(command.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
