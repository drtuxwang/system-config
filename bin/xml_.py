#!/usr/bin/env python3
"""
Convert BSON/JSON/XML/YAML to XML file.
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

    def get_compact_flag(self) -> bool:
        """
        Return compact flag.
        """
        return self._args.compact_flag

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
            help="Check XML configuration files for errors.",
        )
        parser.add_argument(
            '-s',
            dest='compact_flag',
            action='store_true',
            help="Compact XML data on one line.",
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
            command = command_mod.Command('chkxml', errors='stop')
            task = subtask_mod.Task(command.get_cmdline() + paths)
            task.run()
            if task.get_exitcode():
                raise SystemExit(1)

    @staticmethod
    def _convert(paths: List[Path], compact: bool) -> None:
        data = config_mod.Data()
        html_paths = []
        xml_paths = []

        types = config_mod.Data.TYPES
        for path in paths:
            if types.get(path.suffix) == 'XML':
                if path.suffix in ('.htm', '.html', '.xhtml'):
                    html_paths.append(path)
                else:
                    xml_paths.append(path)
                continue

            try:
                data.read(path)
            except config_mod.ReadConfigError as exception:
                raise SystemExit(f"{path}: {exception}") from exception
            xml_path = path.with_suffix('.xml')
            print(f'Converting "{path}" to "{xml_path}"...')
            try:
                data.write(xml_path, compact)
            except config_mod.WriteConfigError as exception:
                raise SystemExit(f"{path}: {exception}") from exception

        if html_paths:
            command = command_mod.Command('htmlformat', errors='stop')
            task = subtask_mod.Task(command.get_cmdline() + html_paths)
            task.run()
            if task.get_exitcode():
                raise SystemExit(1)

        if xml_paths:
            command = command_mod.Command('xmlformat', errors='stop')
            task = subtask_mod.Task(command.get_cmdline() + xml_paths)
            task.run()
            if task.get_exitcode():
                raise SystemExit(1)

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()
        check = options.get_check_flag()
        compact = options.get_compact_flag()

        paths = [Path(x) for x in options.get_files()]
        for path in paths:
            if not path.exists():
                raise SystemExit(f'{sys.argv[0]}: Cannot find "{path}" file.')

        types = config_mod.Data.TYPES
        if check:
            cls._check([x for x in paths if types.get(x.suffix) == 'XML'])
        else:
            cls._convert([x for x in paths if x.suffix in types], compact)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
