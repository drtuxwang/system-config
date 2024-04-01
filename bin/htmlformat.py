#!/usr/bin/env python3
"""
Re-format XHTML file.
"""

import argparse
import os
import re
import signal
import sys
from pathlib import Path
from typing import List

import bs4  # type: ignore

from command_mod import Command
from subtask_mod import Batch


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
        parser = argparse.ArgumentParser(description="Re-format XHTML file.")

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File to change.",
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
    _xmllint = Command('xmllint', errors='stop')

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
    def _sub(text: str) -> str:
        subs = {'\xa0': '&#160;', '<': '&lt;', '>': '&gt;'}
        issub = re.compile('|'.join(map(re.escape, subs)))
        return issub.sub(
            lambda x: subs[x.group(0)],
            text.replace('&', '&amp;')
        )

    @classmethod
    def _reformat(cls, path: Path) -> None:
        try:
            old_xhtml = path.read_bytes()
        except OSError as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot read "{path}" file.',
            ) from exception

        soup = bs4.BeautifulSoup(old_xhtml, 'html.parser')
        new_xhtml = soup.prettify(formatter=bs4.formatter.HTMLFormatter(
            entity_substitution=cls._sub,
            indent=2,
        )).encode()

        if new_xhtml != old_xhtml:
            print(f'Formatting "{path}" XHTML file...')
            path_new = Path(f'{path}.part')
            try:
                path_new.write_bytes(new_xhtml)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create "{path_new}" file.',
                ) from exception
            try:
                path_new.replace(path)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: '
                    f'Cannot rename "{path_new}" file to "{path}".',
                ) from exception

    @classmethod
    def run(cls) -> bool:
        """
        Start program
        """
        options = Options()

        errors = False
        for path in [Path(x) for x in options.get_files()]:
            if path.is_file() and path.suffix in ('.htm', '.html', '.xhtml'):
                task = Batch(cls._xmllint.get_cmdline() + [path])
                task.run()
                if task.has_error():
                    for line in task.get_error():
                        print(line, file=sys.stderr)
                    errors = True
                else:
                    cls._reformat(path)

        return errors


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
