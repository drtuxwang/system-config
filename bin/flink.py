#!/usr/bin/env python3
"""
Recursively link all files.
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


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getDirectories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Recursively link all files.')

        parser.add_argument('directories', nargs='+', metavar='directory',
                            help='Directory containing files to link.')

        self._args = parser.parse_args(args)

        for directory in self._args.directories:
            if not os.path.isdir(directory):
                raise SystemExit(
                    sys.argv[0] + ': Source directory "' + directory + '" does not exist.')
            elif os.path.samefile(directory, os.getcwd()):
                raise SystemExit(sys.argv[0] + ': Source directory "' + directory +
                                 '" cannot be current directory.')


class Link:

    def __init__(self, options):
        for directory in options.getDirectories():
            self._linkFiles(directory, '.')

    def _linkFiles(self, sourceDir, targetDir, subdir=''):
        try:
            sourceFiles = sorted([os.path.join(sourceDir, x) for x in os.listdir(sourceDir)])
        except PermissionError:
            return
        if not os.path.isdir(targetDir):
            print('Creating "' + targetDir + '" directory...')
            try:
                os.mkdir(targetDir)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' + targetDir + '" directory.')

        for sourceFile in sorted(sourceFiles):
            targetFile = os.path.join(targetDir, os.path.basename(sourceFile))
            if os.path.isdir(sourceFile):
                self._linkFiles(sourceFile, targetFile, os.path.join(os.pardir, subdir))
            else:
                if os.path.islink(targetFile):
                    print('Updating "' + targetFile + '" link...')
                    try:
                        os.remove(targetFile)
                    except OSError:
                        raise SystemExit(sys.argv[0] + ': Cannot remove "' + targetFile + '" link.')
                else:
                    print('Creating "' + targetFile + '" link...')
                try:
                    if os.path.isabs(sourceFile):
                        os.symlink(sourceFile, targetFile)
                    else:
                        os.symlink(os.path.join(subdir, sourceFile), targetFile)
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + targetFile + '" link.')


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
