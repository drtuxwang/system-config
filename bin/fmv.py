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

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

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
                shutil.move(source, target)
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
            shutil.move(source, target)
        except OSError:
            if os.path.isdir(source):
                raise SystemExit(sys.argv[0] + ': Cannot rename "' + source + '" source directory.')
            else:
                raise SystemExit(sys.argv[0] + ': Cannot rename "' + source + '" source file.')

    def run(self):
        """
        Start program
        """
        self._options = Options()
        sources = self._options.get_sources()
        target = self._options.get_target()

        if len(sources) > 1 or os.path.isdir(target):
            self._move()
        else:
            self._rename(sources[0], target)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
