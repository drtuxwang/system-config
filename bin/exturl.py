#!/usr/bin/env python3
"""
Extracts http references from a HTML file.
"""

import argparse
import glob
import os
import re
import signal
import sys
import urllib.parse
from typing import List


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
            description="Extracts http references from a HTML file.",
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

    def _extract(self, file: str) -> List[str]:
        try:
            with open(file, encoding='utf-8', errors='replace') as ifile:
                urls = []
                for line in ifile:
                    line = line.strip()
                    for token in self._is_iframe.sub('href=', line).split():
                        if (
                                self._is_url.match(token) and
                                not self._is_ignore.search(token)
                        ):
                            url = token[5:].split('>')[0]
                            for quote in ('"', "'"):
                                if quote in url:
                                    url = url.split(quote)[1]
                            urls.append(url)
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read {file} HTML file.',
            ) from exception
        return urls

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        urls = []
        self._is_iframe = re.compile('<iframe.*src=', re.IGNORECASE)
        self._is_ignore = re.compile('mailto:|#', re.IGNORECASE)
        self._is_url = re.compile(r'href=.*[\'">]|onclick=.*\(', re.IGNORECASE)

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot find "{file}" HTML file.',
                )
            urls.extend(self._extract(file))
        for url in sorted(set(urls)):
            print(urllib.parse.unquote(url))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
