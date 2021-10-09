#!/usr/bin/env python3
"""
Extracts Javascript from a HTML file.
"""

import argparse
import glob
import os
import signal
import sys
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
            description='Extracts Javascript from a HTML file.',
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='HTML file.'
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
            sys.exit(exception)

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
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @staticmethod
    def _extract(file: str) -> Generator[str, None, None]:
        lines = []
        try:
            with open(file, encoding='utf-8', errors='replace') as ifile:
                for line in ifile:
                    lines.append(line.strip().replace('&gt;', '>').replace(
                        '&lt;', '<').replace('SCRIPT>', 'script>'))
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot read ' + file + ' HTML file.'
            ) from exception

        for match in ' '.join(lines).split('<script>')[1:]:
            yield match.split('</script>')[0]

    @staticmethod
    def _write(file: str, script: str) -> None:
        lines = jsbeautifier.beautify(script).splitlines()
        print('Writing "{0:s}" with {1:d} lines...'.format(file, len(lines)))
        try:
            with open(file, 'w', encoding='utf-8') as ofile:
                for line in lines:
                    print(line, file=ofile)
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot write "' + file +
                '" configuration file.'
            ) from exception

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" HTML file.')
            number = 0
            for script in cls._extract(file):
                number += 1
                jsfile = '{0:s}-{1:02d}.js'.format(
                    file.rsplit('.', 1)[0], number)
                cls._write(jsfile, script)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
