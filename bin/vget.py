#!/usr/bin/env python3
"""
Video downloader for Youtube & compatible websites (uses youtube-dl).
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_youtubedl(self):
        """
        Return youtubedl Command class object.
        """
        return self._youtubedl

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Video downloader for Youtube & compatible websites.')

        parser.add_argument(
            '-f',
            nargs=1,
            dest='code',
            default=None,
            help='Select video format code (default prefer 720 height).'
        )
        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='Show video format codes.'
        )
        parser.add_argument(
            '-O',
            nargs=1,
            dest='output',
            default=None,
            help='Output file name.'
        )
        parser.add_argument(
            'url',
            nargs=1,
            help='Youtube or compatible video URL.'
        )

        self._args = parser.parse_args(args)

    def _detect_code(self, url):
        task = subtask_mod.Batch(
            self._youtubedl.get_cmdline() + ['--list-formats', url]
        )
        task.run(pattern=r'^[^ ]+ +mp4 +\d+x\d+ ')

        codes = {}
        for line in task.get_output():
            if 'video only' not in line:
                code, _, size = line.split()[:3]
                codes[int(size.split('x')[1])] = code
        for height in sorted(codes, reverse=True):
            if height <= 720:
                return codes[height]
        for height in sorted(codes):
            return codes[height]

        raise SystemExit(sys.argv[0] + ': No video stream: ' + url)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        url = self._args.url[0]
        if '&index=' in url:  # Fix download one video for series
            url = url.split('&')[0]
        self._youtubedl = command_mod.CommandFile(sys.executable)
        self._youtubedl.set_args(['-m', 'youtube_dl', '--playlist-end', '1'])
        if self._args.view_flag:
            self._youtubedl.append_arg('--list-formats')
        else:
            if self._args.code:
                code = self._args.code[0]
            else:
                code = self._detect_code(url)
            self._youtubedl.extend_args(['--format', code])
            if self._args.output:
                self._youtubedl.extend_args(['--output', self._args.output[0]])

        self._youtubedl.append_arg(url)


class Main:
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
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
    def run():
        """
        Start program
        """
        options = Options()

        subtask_mod.Exec(options.get_youtubedl().get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
