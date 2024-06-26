#!/usr/bin/env python3
"""
Streaming video downloader using VLC.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from subtask_mod import Task


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_output(self) -> Path:
        """
        Return output file.
        """
        return self._output

    def get_url(self) -> str:
        """
        Return URL.
        """
        return self._args.url[0]

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Streaming video downloader using VLC.",
        )
        parser.add_argument(
            '-O',
            nargs=1,
            dest='output',
            default=None,
            help="Output file name.",
        )
        parser.add_argument(
            'url',
            nargs=1,
            help="Video URL.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.output:
            self._output = Path(self._args.output[0]).with_suffix('.mpegts')
        else:
            path = Path(self._args.url[0])
            self._output = Path(f'{path.name[:31]}.mpegts')

        if self._output.exists():
            raise SystemExit(f"Output file already exists: {self._output}")


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
    def run() -> int:
        """
        Start program
        """
        options = Options()
        url = options.get_url()
        path = options.get_output()
        path_new = Path(f'{path}.part')

        vlc = Command('cvlc', errors='stop')
        vlc.set_args(
            ['-v', '--sout', f'file/ts:{path_new}', url, 'vlc://quit']
        )
        task = Task(vlc.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(task.get_exitcode())

        mp4 = Command('mp4', errors='stop')
        mp4.set_args([path.with_suffix('.mp4'), path_new])
        task = Task(mp4.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(task.get_exitcode())

        path_new.unlink()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
