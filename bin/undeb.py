#!/usr/bin/env python3
"""
Unpack a compressed archive in DEB format.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import Any, List

from subtask_mod import Batch, Task
from command_mod import Command


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_archives(self) -> List[str]:
        """
        Return list of archives.
        """
        return self._args.archives

    def get_view_flag(self) -> bool:
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unpack a compressed archive in DEB format.",
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="Show contents of archive.",
        )
        parser.add_argument(
            'archives',
            nargs='+',
            metavar='file.deb',
            help="Archive file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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

        os.umask(0o022)

    @staticmethod
    def _remove(*files: Any) -> None:
        for file in files:
            try:
                os.remove(file)
            except OSError:
                pass

    def _unpack(self, file: str) -> None:
        task = Batch(self._ar.get_cmdline() + ['t', file])
        task.run(pattern='(data|control).tar')
        if len(task.get_output()) != 2:
            raise SystemExit(f'{sys.argv[0]}: Cannot read "{file}" DEB file.')
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                f'received from "{task.get_file()}".',
            )
        data_file = task.get_output('data.tar.*')[-1]
        control_file = task.get_output('control.tar.*')[-1]

        task = Batch(self._ar.get_cmdline() + ['x', file, data_file])
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                f'received from "{task.get_file()}".',
            )
        task2 = Task(self._tar.get_cmdline() + [data_file])
        task2.run()
        self._remove(data_file)
        if task2.get_exitcode():
            raise SystemExit(
                f'{sys.argv[0]}: Error code {task2.get_exitcode()} '
                f'received from "{task2.get_file()}".',
            )

        task = Batch(self._ar.get_cmdline() + ['x', file, control_file])
        task.run()
        if self._options.get_view_flag():
            task2 = Task(self._tar.get_cmdline() + [control_file])
            task2.run(replace=(os.curdir, 'DEBIAN'))
        else:
            if not Path('DEBIAN').is_dir():
                try:
                    Path('DEBIAN').mkdir()
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot create "DEBIAN" directory.',
                    ) from exception
            task2 = Task(
                self._tar.get_cmdline() + [Path(os.pardir, control_file)]
            )
            task2.run(directory='DEBIAN', replace=(os.curdir, 'DEBIAN'))
        self._remove(control_file)

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._options = options
        self._ar = Command('ar', errors='stop')
        self._tar = Command('tar', errors='stop')
        if options.get_view_flag():
            self._tar.set_args(['tf'])
        else:
            self._tar.set_args(['xf'])
        for path in [Path(x) for x in options.get_archives()]:
            if not path.is_file():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{path}" DEB file.',
                )
            self._unpack(str(path))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
