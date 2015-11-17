#!/usr/bin/env python3
"""
Create links to JPEG files.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getDirectorys(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Create links to JPEG files.')

        parser.add_argument('directories', nargs='+', metavar='directory',
                            help='Directory containing JPEG files to link.')

        self._args = parser.parse_args(args)

        for directory in self._args.directories:
            if not os.path.isdir(directory):
                raise SystemExit(
                    sys.argv[0] + ': Source directory "' + directory + '" does not exist.')
            elif os.path.samefile(directory, os.getcwd()):
                raise SystemExit(sys.argv[0] + ': Source directory "' + directory +
                                 '" cannot be current directory.')


class Link(syslib.Dump):

    def __init__(self, options):
        for directory in options.getDirectorys():
            for file in sorted(glob.glob(os.path.join(directory, '*'))):
                if (file.split('.')[-1].lower() in (
                        'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pcx', 'svg', 'tif', 'tiff')):
                    link = os.path.basename(directory + '_' + os.path.basename(file))
                    if not os.path.islink(link):
                        try:
                            os.symlink(file, link)
                        except OSError:
                            raise SystemExit(sys.argv[0] + ': Cannot create "' + link + '" link.')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Link(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windowsArgv(self):
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
