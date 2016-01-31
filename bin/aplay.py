#!/usr/bin/env python3
"""
Play MP3/OGG/WAV audio files in directory.
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


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

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
        parser = argparse.ArgumentParser(description='Play MP3/OGG/WAV audio files in directory.')

        parser.add_argument('-s', dest='shuffleFlag', action='store_true',
                            help='Shuffle order of the media files.')
        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='View information.')
        parser.add_argument('directories', nargs='+', metavar='directory',
                            help='Audio directory.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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
        except (syslib.SyslibError, SystemExit) as exception:
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
    def _getfiles(directory, *patterns):
        files = []
        for pattern in patterns:
            files.extend(glob.glob(os.path.join(directory, pattern)))
        return sorted(files)

    def run(self):
        """
        Start program
        """
        options = Options()

        play = syslib.Command('play')
        if options.get_view_flag():
            play.set_flags(['-v'])
        for directory in options.get_directories():
            if not os.path.isdir(directory):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + directory + '" media directory.')
            files = self._getfiles(directory, '*.mp3', '*.ogg', '*.wav')
            if options.get_shuffle_flag():
                random.shuffle(files)
            play.extend_args(files)

        play.run()
        if play.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(play.get_exitcode()) +
                             ' received from "' + play.get_file() + '".')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
