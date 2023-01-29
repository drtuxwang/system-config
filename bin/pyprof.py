#!/usr/bin/env python3
"""
Profile Python 3.x program.
"""

import argparse
import os
import pstats
import signal
import sys
from pathlib import Path
from typing import List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self._module_args: List[str] = []
        self.parse(sys.argv)

    def get_file(self) -> str:
        """
        Return list of file.
        """
        return self._args.file[0]

    def get_module_args(self) -> List[str]:
        """
        Return module args.
        """
        return self._module_args

    def get_lines(self) -> int:
        """
        Return number of lines.
        """
        return self._args.lines[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Profile Python 3.x program.",
        )

        parser.add_argument(
            '-n',
            nargs=1,
            type=int,
            dest='lines',
            default=[20],
            metavar='K',
            help="Output first K lines.",
        )
        parser.add_argument(
            'file',
            nargs=1,
            metavar='file[.py]|file.pstats',
            help="Python module or pstats file.",
        )

        my_args = []
        while args:
            my_args.append(args[0])
            if not args[0].startswith('-'):
                break
            if args[0] == '-n' and len(args) >= 2:
                args = args[1:]
                my_args.append(args[0])
            args = args[1:]

        self._args = parser.parse_args(my_args)

        self._module_args = args[1:]

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

    @staticmethod
    def _get_command(
        module_file: str,
        module_args: List[str],
    ) -> command_mod.Command:
        if Path(module_file).is_file():
            return command_mod.CommandFile(module_file, args=module_args)

        try:
            return command_mod.Command(module_file, args=module_args)
        except command_mod.CommandNotFoundError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find "{module_file}" module file',
            ) from exception

    @classmethod
    def _profile(cls, module_file: str, module_args: List[str]) -> str:
        stats_file = Path(module_file).with_suffix('.pstats').name
        if Path(stats_file).is_file():
            try:
                os.remove(stats_file)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot remove old "{stats_file}" file.',
                ) from exception

        python3 = command_mod.CommandFile(sys.executable)
        python3.set_args(['-B', '-m', 'cProfile', '-o', stats_file])

        command = cls._get_command(module_file, module_args)

        task = subtask_mod.Task(python3.get_cmdline() + command.get_cmdline())
        task.run()

        print(f"pyprof: {command.args2cmd([command.get_file()])}{module_args}")
        return stats_file

    @staticmethod
    def _show(stats_file: str, lines: int) -> None:
        try:
            stats = pstats.Stats(stats_file)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{stats_file}" file.',
            ) from exception

        stats.strip_dirs().sort_stats('tottime', 'cumtime').print_stats(lines)

    def run(self) -> int:
        """
        Start program
        """
        self._options = Options()
        file = self._options.get_file()

        if not file.endswith('.pstats'):
            if not file.endswith('.py'):
                file = file + '.py'
            file = self._profile(file, self._options.get_module_args())

        self._show(file, self._options.get_lines())

        file = self._options.get_file()

        if not file.endswith('.pstats'):
            if not file.endswith('.py'):
                file = file + '.py'
            file = self._profile(file, self._options.get_module_args())

        self._show(file, self._options.get_lines())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
