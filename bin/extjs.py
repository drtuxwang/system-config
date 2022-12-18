#!/usr/bin/env python3
"""
Extracts Javascript from a HTML file.
"""

import argparse
import glob
import os
import signal
import sys
from pathlib import Path
from typing import Generator, List

import jsbeautifier  # type: ignore


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Extracts Javascript from a HTML file.",
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="HTML file.",
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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def _extract(path: Path) -> Generator[str, None, None]:
        lines = []
        try:
            with path.open(encoding='utf-8', errors='replace') as ifile:
                for line in ifile:
                    lines.append(line.strip().replace('&gt;', '>').replace(
                        '&lt;', '<').replace('SCRIPT>', 'script>'))
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read {path} HTML file.',
            ) from exception

        for match in ' '.join(lines).split('<script>')[1:]:
            yield match.split('</script>')[0]

    @staticmethod
    def _write(path: Path, script: str) -> None:
        lines = jsbeautifier.beautify(script).splitlines()
        print(f'Writing "{path}" with {len(lines)} lines...')
        try:
            with path.open('w', encoding='utf-8') as ofile:
                for line in lines:
                    print(line, file=ofile)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot write "{path}" configuration file.',
            ) from exception

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        for path in [Path(x) for x in options.get_files()]:
            if not path.is_file():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{path}" HTML file.',
                )
            number = 0
            for script in cls._extract(path):
                number += 1
                jsfile = f"{str(path).rsplit('.', 1)[0]}-{number:02d}.js"
                cls._write(Path(jsfile), script)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
