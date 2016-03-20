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

    def get_directories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def get_shuffle_flag(self):
        """
        Return shuffle flag.
        """
        return self._args.shuffle_flag

    def get_view_flag(self):
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Play AVI/FLV/MP4 video files in directory.')

        parser.add_argument('-s', dest='shuffle_flag', action='store_true',
                            help='Shuffle order of the media files.')
        parser.add_argument('-v', dest='view_flag', action='store_true',
                            help='View information.')
        parser.add_argument('directories', nargs='+', metavar='directory',
                            help='Video directory.')

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

        play = command_mod.Command('play', errors='stop')
        if options.get_view_flag():
            play.set_args(['-v'])
        for directory in options.get_directories():
            if not os.path.isdir(directory):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + directory + '" media directory.')
            files = self._getfiles(directory, '*.avi', '*.flv', '*.mp4')
            if options.get_shuffle_flag():
                random.shuffle(files)
            play.extend_args(files)

        task = subtask_mod.Task(play.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                             ' received from "' + task.get_file() + '".')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
