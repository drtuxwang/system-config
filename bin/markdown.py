#!/usr/bin/env python3
"""
Wrapper for "markdown2" command
"""

import argparse
import re
import signal
import sys
from pathlib import Path
from typing import List

import bs4  # type: ignore
import markdown2  # type: ignore


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
            description="Convert Markdown files to valid XHTML.")

        parser.add_argument(
            'files',
            nargs='*',
            metavar='file',
            help="File to search.",
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

    @staticmethod
    def _sub(text: str) -> str:
        subs = {'\xa0': '&#160;', '<': '&lt;', '>': '&gt;'}
        issub = re.compile('|'.join(map(re.escape, subs)))
        return issub.sub(
            lambda x: subs[x.group(0)],
            text.replace('&', '&amp;')
        )

    @classmethod
    def _reformat(cls, data: str) -> bytes:
        if '<h1>' in data and '</h1>' in data:
            title = data.split('<h1>', 1)[1].split('</h1>', 1)[0]
        else:
            title = 'Untitled Document'
        old_xhtml = (
            '<!DOCTYPE html>\n<html lang="en" xml:lang="en" '
            'xmlns="http://www.w3.org/1999/xhtml">\n'
            f'<head>\n<title>{title}</title>\n</head>\n<body>\n' +
            data + '</body>\n</html>'
        )

        soup = bs4.BeautifulSoup(old_xhtml, 'html.parser')
        return soup.prettify(formatter=bs4.formatter.HTMLFormatter(
            entity_substitution=cls._sub,
            indent=2,
        )).encode()

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        markdowner = markdown2.Markdown(extras=['fenced-code-blocks'])
        for path in [Path(x) for x in Options().get_files()]:
            if path.exists and path.suffix == '.md':
                try:
                    data = markdowner.convert(path.read_text(errors='replace'))
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot read "{path}" file.'
                    ) from exception

                path_new = path.with_suffix('.xhtml')
                print(f'Converting "{path}" to "{path_new}"...')
                new_xhtml = cls._reformat(data)
                try:
                    path_new.write_bytes(new_xhtml)
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot write "{path_new}" file.'
                    ) from exception

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
