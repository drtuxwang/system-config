#!/usr/bin/env python3
"""
Youtube video downloader.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
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
            description='Youtube video downloader.')

        parser.add_argument(
            '-s',
            nargs=1,
            type=int,
            dest='height',
            metavar='height',
            default=360,
            help='Select video height (default 360).'
        )
        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='Show video format codes.'
        )
        parser.add_argument(
            'urls',
            nargs='+',
            metavar='url',
            help='Youtube video URL.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._youtubedl = command_mod.CommandFile(sys.executable)
        self._youtubedl.set_args(['-m', 'youtube_dl'])

        if self._args.view_flag:
            self._youtubedl.extend_args(['--list-formats'])
        elif self._args.height:
            self._youtubedl.extend_args([
                '--format',
                'bestvideo[ext=mp4][height={0:d}]+bestaudio[ext=m4a]/'
                'best[height<=480]'.format(self._args.height)
            ])
        self._youtubedl.extend_args(self._args.urls)


class Main(object):
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
