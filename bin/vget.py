#!/usr/bin/env python3
"""
Streaming video downloader using yt-dlp.
"""

import argparse
import os
import signal
import sys
import time
import urllib.request
from pathlib import Path
from typing import List

from command_mod import Command
from config_mod import Config
from subtask_mod import Batch, Task


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self._mtime: float = 0
        self._output = ''
        self.parse(sys.argv)

    def get_mtime(self) -> float:
        """
        Return output file modification time.
        """
        return self._mtime

    def get_output(self) -> str:
        """
        Return output file.
        """
        return self._output

    def get_vget(self) -> Command:
        """
        Return vget Command class object.
        """
        return self._vget

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Streaming video downloader using yt-dlp."
        )
        parser.add_argument(
            '-f',
            nargs=1,
            dest='code',
            default=None,
            help='Select video format code (default "136+140/mp4" for 720p).',
        )
        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="Show video format codes.",
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
            help="Youtube or compatible video URL.",
        )

        self._args = parser.parse_args(args)

    def _detect_code(self, url: str) -> str:
        task = Batch(self._vget.get_cmdline() + ['--list-formats', url])
        task.run(pattern=r'^[^ ]+ +mp4 +\d+x\d+ ')

        codes = {}
        for line in task.get_output():
            if 'mp4' in line and 'dash' in line:
                code, _, size = line.split()[:3]
                codes[int(size.split('x')[1])] = code
        if not codes:  # No dash workaround
            for line in task.get_output():
                if 'mp4' in line:
                    code, _, size = line.split()[:3]
                    codes[int(size.split('x')[1])] = code
        for height in sorted(codes, reverse=True):
            if height <= 720:
                return codes[height] + '+bestaudio[ext=m4a]/mp4'
        for height in sorted(codes):
            return codes[height] + '+bestaudio[ext=m4a]/mp4'

        raise SystemExit(f"{sys.argv[0]}: No video stream: {url}")

    def _detect_mtime(self, url: str) -> float:
        task = Batch(self._vget.get_cmdline() + ['--get-url', url])
        task.run(pattern=r'^http')
        if task.has_output():
            try:
                req = urllib.request.Request(task.get_output()[0], headers={
                    'User-Agent': Config().get('web_agent'),
                })
            except (urllib.error.HTTPError, urllib.error.URLError):
                pass
            else:
                with urllib.request.urlopen(req) as conn:
                    info = conn.info()
                try:
                    return time.mktime(time.strptime(
                        info.get('Last-Modified'),
                        '%a, %d %b %Y %H:%M:%S %Z',
                    ))
                except TypeError:
                    pass

        return 0

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        url = self._args.url[0]
        if '&index=' in url:  # Fix download one video for series
            url = url.split('&')[0]
        self._vget = Command('yt-dlp')
        self._vget.set_args(['--playlist-end', '1'])

        if self._args.view_flag:
            self._vget.extend_args(['--list-formats', url])
            return

        if self._args.code:
            code = self._args.code[0]
        elif url.endswith('.m3u8'):  # Multi part streaming
            code = '0'
        else:
            code = self._detect_code(url)
        self._vget.extend_args(['--format', code])

        self._mtime = self._detect_mtime(url)

        if self._args.output:
            self._output = self._args.output[0]
            if Path(self._output).is_file():
                raise SystemExit(f"Output file already exists: {self._output}")
            self._vget.extend_args(['--output', self._output])

        self._vget.append_arg(url)


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
        mtime = options.get_mtime()
        output = options.get_output()
        vget = options.get_vget()

        task = Task(vget.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(task.get_exitcode())

        if mtime and output:
            os.utime(output, (mtime, mtime))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
