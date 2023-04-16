#!/usr/bin/env python3
"""
Check XML file for errors.
"""

import argparse
import http.client
import os
import signal
import sys
import xml.sax
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
        self.parse(sys.argv)

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def get_view_flag(self) -> bool:
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Check XML file for errors.",
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="View XML data.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="XML/XHTML files.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class XmlDataHandler(xml.sax.ContentHandler):  # type: ignore
    """
    XML data handler class
    """

    def __init__(self, view: bool) -> None:
        super().__init__()
        self._elements: list = []
        self._nelement = 0
        self._view_flag = view

    def startElement(self, name: str, attrs: dict) -> None:
        self._nelement += 1
        self._elements.append(f'{name}({self._nelement})')
        if self._view_flag:
            for (key, value) in attrs.items():
                print(
                    '.'.join(self._elements + [key]), "='", value, "'", sep='')

    def characters(self, content: str) -> None:
        if self._view_flag:
            value = content.replace('\\', '\\\\').replace('\n', '\\n')
            print(
                '.'.join(self._elements + ['text']),
                f"='{value}",
                "'",
                sep=''
            )

    def endElement(self, name: str) -> None:
        self._elements.pop()


class Main:
    """
    Main class
    """
    _xmllint = command_mod.Command('xmllint', args=['--noout'], errors='stop')

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

    @classmethod
    def run(cls) -> bool:
        """
        Start program
        """
        options = Options()

        handler = XmlDataHandler(options.get_view_flag())
        for path in [Path(x) for x in options.get_files()]:
            if not path.is_file():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot open "{path}" XML file.',
                )

            print(f'Checking "{path}" XML file...')
            task = subtask_mod.Batch(cls._xmllint.get_cmdline() + [path])
            task.run(pattern=": parser warning : Unsupported version '1.1'")
            errors = [
                x
                for x in task.get_error()
                if ': parser warning : Unsupported' not in x
            ]
            for line in errors:
                print(line, file=sys.stderr)

            try:
                with path.open(errors='replace') as ifile:
                    xml.sax.parse(ifile, handler)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot parse "{path}" XML file.',
                ) from exception
            except http.client.HTTPException as exception:
                raise SystemExit(
                    f"{sys.argv[0]}: HTTP request failed.",
                ) from exception
            except Exception as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Invalid "{path}" XML file.',
                ) from exception

        return bool(errors)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
