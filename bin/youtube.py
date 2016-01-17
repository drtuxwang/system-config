#!/usr/bin/env python3
"""
Youtube video downloader.
"""

import argparse
import glob
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

        self._youtubedl = syslib.Command('youtube-dl', check=False)
        if not self._youtubedl.is_found():
            youtube = syslib.Command('youtube', args=args[1:], check=False)
            if youtube.is_found():
                youtube.run(mode='exec')
            self._youtubedl = syslib.Command('youtube-dl')

        if self._args.viewFlag:
            self._youtubedl.set_args(['--list-formats'])
        elif self._args.format:
            self._youtubedl.set_args(['--title', '--format', str(self._args.format[0])])
        self._youtubedl.extend_args(self._args.urls)

        self._setpython(self._youtubedl)

    def get_youtubedl(self):
        """
        Return youtubedl Command class object.
        """
        return self._youtubedl

    def _setpython(self, command):  # Must use system Python
        if os.path.isfile('/usr/bin/python3'):
            command.set_wrapper(syslib.Command(file='/usr/bin/python3'))
        elif os.path.isfile('/usr/bin/python'):
            command.set_wrapper(syslib.Command(file='/usr/bin/python'))

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Youtube video downloader.')

        parser.add_argument('-f', nargs=1, type=int, dest='format', metavar='code',
                            help='Select video format code.')
        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='Show video format codes.')

        parser.add_argument('urls', nargs='+', metavar='url', help='Youtube video URL.')

        self._args = parser.parse_args(args)


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
            options.get_youtubedl().run()
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
