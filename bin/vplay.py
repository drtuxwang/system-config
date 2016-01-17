#!/usr/bin/env python3
"""
Play AVI/FLV/MP4 files in directory.
"""

import argparse
import glob
import random
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

    def get_directories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def get_shuffle_flag(self):
        """
        Return shuffle flag.
        """
        return self._args.shuffleFlag

    def get_view_flag(self):
        """
        Return view flag.
        """
        return self._args.viewFlag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Play AVI/FLV/MP4 video files in directory.')

        parser.add_argument('-s', dest='shuffleFlag', action='store_true',
                            help='Shuffle order of the media files.')
        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='View information.')
        parser.add_argument('directories', nargs='+', metavar='directory',
                            help='Video directory.')

        self._args = parser.parse_args(args)


class Play(object):
    """
    Play class
    """

    def __init__(self, options):
        self._play = syslib.Command('play')

        if options.get_view_flag():
            self._play.set_flags(['-v'])
        for directory in options.get_directories():
            if not os.path.isdir(directory):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + directory + '" media directory.')
            files = self._getfiles(directory, '*.avi', '*.flv', '*.mp4')
            if options.get_shuffle_flag():
                random.shuffle(files)
            self._play.extend_args(files)

    def run(self):
        self._play.run()
        if self._play.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._play.get_exitcode()) +
                             ' received from "' + self._play.get_file() + '".')

    def _getfiles(self, directory, *patterns):
        files = []
        for pattern in patterns:
            files.extend(glob.glob(os.path.join(directory, pattern)))
        return sorted(files)


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            Play(options).run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
