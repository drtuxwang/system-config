#!/usr/bin/env python3
"""
Move or rename files.
"""

import argparse
import glob
import os
import shutil
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

    def get_overwrite_flag(self):
        """
        Return overwrite flag.
        """
        return self._args.overwriteFlag

    def get_sources(self):
        """
        Return list of source files.
        """
        return self._args.sources

    def get_target(self):
        """
        Return target file or directory.
        """
        return self._args.target[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Move or rename files.')

        parser.add_argument('-f', dest='overwriteFlag', action='store_true',
                            help='Overwrite files.')

        parser.add_argument('sources', nargs='+', metavar='source',
                            help='Source file or directory.')
        parser.add_argument('target', nargs=1, metavar='target',
                            help='Target file or directory.')

        self._args = parser.parse_args(args)


class Move(object):
    """
    Move class
    """

    def __init__(self, options):
        self._options = options
        if len(options.get_sources()) > 1 or os.path.isdir(options.get_target()):
            self._move()
        else:
            self._rename(options.get_sources()[0], options.get_target())

    def _move(self):
        if not os.path.isdir(self._options.get_target()):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + self._options.get_target() +
                '" target directory.')
        for source in self._options.get_sources():
            if os.path.isdir(source):
                print('Moving "' + source + '" directory...')
            elif os.path.isfile(source):
                print('Moving "' + source + '" file...')
            else:
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + source + '" source file or directory.')
            target = os.path.join(self._options.get_target(), os.path.basename(source))
            if os.path.isdir(target):
                raise SystemExit(
                    sys.argv[0] + ': Cannot safely overwrite "' + target + '" target directory.')
            elif os.path.isfile(target):
                if not self._options.get_overwrite_flag():
                    raise SystemExit(
                        sys.argv[0] + ': Cannot safely overwrite "' + target + '" target file.')
            try:
                os.rename(source, target)
            except OSError as exception:
                if 'Invalid cross-device link' in exception.args:
                    self._cprm(source, target)
                elif os.path.isdir(source):
                    raise SystemExit(
                        sys.argv[0] + ': Cannot move "' + source + '" source directory.')
                else:
                    raise SystemExit(sys.argv[0] + ': Cannot move "' + source + '" source file.')

    def _cprm(self, source, target):
        if os.path.isdir(source):
            try:
                shutil.copytree(source, target, symlinks=True)
            except IOError:
                raise SystemExit(sys.argv[0] + ': Cannot copy "' + source + '" source file.')
            try:
                shutil.rmtree(source)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot move "' + source + '" source directory.')
        else:
            try:
                shutil.copy2(source, target)
            except IOError as exception:
                if exception.args != (95, 'Operation not supported'):  # os.listxattr for ACL
                    raise SystemExit(sys.argv[0] + ': Cannot copy "' + source + '" source file.')
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot read "' + source + '" file.')
            try:
                os.remove(source)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot move "' + source + '" source file.')

    def _rename(self, source, target):
        if os.path.isdir(source):
            print('Renaming "' + source + '" directory...')
        elif os.path.isfile(source):
            print('Renaming "' + source + '" file...')
        else:
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + source + '" source file or directory.')
        if os.path.isdir(target):
            raise SystemExit(
                sys.argv[0] + ': Cannot safely overwrite "' + target + '" target directory.')
        elif os.path.isfile(target):
            if not self._options.get_overwrite_flag():
                raise SystemExit(
                    sys.argv[0] + ': Cannot safely overwrite "' + target + '" target file.')

        try:
            # Workaround Windows rename bug
            if syslib.info.get_system() == 'windows' and os.path.isfile(target):
                os.remove(target)
            os.rename(source, target)
        except OSError:
            if os.path.isdir(source):
                raise SystemExit(sys.argv[0] + ': Cannot rename "' + source + '" source directory.')
            else:
                raise SystemExit(sys.argv[0] + ': Cannot rename "' + source + '" source file.')


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
            Move(options)
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
