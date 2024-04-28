#!/usr/bin/env python3
"""
Uncompress a file in XZ format.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from file_mod import FileStat
from subtask_mod import Batch


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_archives(self) -> List[str]:
        """
        Return archive files.
        """
        return self._args.archives

    def get_command(self) -> Command:
        """
        Return xz Command class object.
        """
        return self._command

    @staticmethod
    def _set_libraries(command: Command) -> None:
        libdir = Path(Path(command.get_file()).parent, 'lib')
        if Path(libdir).is_dir() and os.name == 'posix':
            if os.uname()[0] == 'Linux':
                if 'LD_LIBRARY_PATH' in os.environ:
                    os.environ['LD_LIBRARY_PATH'] = (
                        f"{libdir}{os.pathsep}{os.environ['LD_LIBRARY_PATH']}"
                    )
                else:
                    os.environ['LD_LIBRARY_PATH'] = str(libdir)

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Uncompress a file in XZ format.",
        )

        parser.add_argument(
            'archives',
            nargs='+',
            metavar='file.xz',
            help="Archive file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._command = Command('xz', args=['-d', '--stdout'], errors='stop')
        self._set_libraries(self._command)


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
        options = Options()

        cmdline = options.get_command().get_cmdline()
        for path in [Path(x) for x in options.get_archives()]:
            if path.suffix == '.xz' and path.is_file():
                print(f"{path}:")

                output = path.stem
                task = Batch(cmdline + [path])
                task.run(file=output)
                if task.get_exitcode():
                    for line in task.get_error():
                        print(line, file=sys.stderr)
                    raise SystemExit(1)

                file_stat = FileStat(path)
                os.chmod(output, file_stat.get_mode())
                file_time = file_stat.get_mtime()
                os.utime(output, (file_time, file_time))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
