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
        parser = argparse.ArgumentParser(description='Youtube video downloader.')

        parser.add_argument('-f', nargs=1, type=int, dest='format', metavar='code',
                            help='Select video format code.')
        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='Show video format codes.')

        parser.add_argument('urls', nargs='+', metavar='url', help='Youtube video URL.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._youtubedl = command_mod.Command('youtube-dl', errors='ignore')
        if not self._youtubedl.is_found():
            youtube = command_mod.Command('youtube', args=args[1:], errors='ignore')
            if youtube.is_found():
                subtask.Exec(youtube.get_cmdline()).run()
            self._youtubedl = command_mod.Command('youtube-dl', errors='stop')

        if self._args.viewFlag:
            self._youtubedl.set_args(['--list-formats'])
        elif self._args.format:
            self._youtubedl.set_args(['--title', '--format', str(self._args.format[0])])
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
