#!/usr/bin/env python3
"""
Convert BSON/JSON/XML/YAML to YAML file.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

import command_mod
import config_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_check_flag(self) -> bool:
        """
        Return check flag.
        """
        return self._args.check_flag

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Convert BSON/JSON/XML/YAML to YAML file.",
        )

        parser.add_argument(
            '-c',
            dest='check_flag',
            action='store_true',
            help="Check YAML configuration files for errors.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File to convert.",
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

    @staticmethod
    def _check(paths: List[Path]) -> None:
        if paths:
            command = command_mod.Command('chkconfig', errors='stop')
            task = subtask_mod.Task(command.get_cmdline() + paths)
            task.run()
            if task.get_exitcode():
                raise SystemExit(1)

    @staticmethod
    def _convert(paths: List[Path]) -> None:
        data = config_mod.Data()

        for path in paths:
            try:
                data.read(path)
            except config_mod.ReadConfigError as exception:
                raise SystemExit(f"{path}: {exception}") from exception
            yaml_path = path.with_suffix('.yaml')
            print(f'Converting "{path}" to "{yaml_path}"...')
            try:
                data.write(yaml_path)
            except config_mod.WriteConfigError as exception:
                raise SystemExit(f"{path}: {exception}") from exception

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()
        check = options.get_check_flag()

        paths = [Path(x) for x in options.get_files()]
        for path in paths:
            if not path.exists():
                raise SystemExit(f'{sys.argv[0]}: Cannot find "{path}" file.')

        types = config_mod.Data.TYPES
        if check:
            cls._check([x for x in paths if types.get(x.suffix) == 'YAML'])
        else:
            cls._convert([x for x in paths if x.suffix in types])

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
