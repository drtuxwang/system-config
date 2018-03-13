#!/usr/bin/env python3
"""
Replace multi-lines patterns in files.
"""

import argparse
import glob
import os
import re
import shutil
import signal
import sys

import file_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def get_pattern(self):
        """
        Return regular expression pattern.
        """
        return self._args.pattern[0]

    def get_replacement(self):
        """
        Return replacement.
        """
        return self._args.replacement[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Replace multi-lines patterns in files.')

        parser.add_argument(
            'pattern',
            nargs=1,
            help='Regular expression.'
        )
        parser.add_argument(
            'replacement',
            nargs=1,
            help='Replacement for matches.'
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='File or directory.'
        )

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
    def _remove(*files):
        for file in files:
            try:
                os.remove(file)
            except OSError:
                pass

    def _replace(self, file):
        newfile = file + '-new'

        try:
            with open(file, errors='replace') as ifile:
                try:
                    with open(newfile, 'w', newline='\n') as ofile:
                        data = ifile.read()
                        data_new = self._is_match.sub(self._replacement, data)
                        print(data_new, end='', file=ofile)
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot create "' + newfile + '" file.'
                    )
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" file.')

        if data_new != data:
            print('{0:s}: changed.'.format(file))
            try:
                os.chmod(newfile, file_mod.FileStat(file).get_mode())
                shutil.move(newfile, file)
            except OSError:
                self._remove(newfile)
                raise SystemExit(
                    sys.argv[0] + ': Cannot update "' + file + '" file.')
        else:
            self._remove(newfile)

    def run(self):
        """
        Start program
        """
        options = Options()

        try:
            self._is_match = re.compile(options.get_pattern())
        except re.error:
            raise SystemExit(
                sys.argv[0] + ': Invalid regular expression "' +
                options.get_pattern() + '".'
            )

        self._replacement = options.get_replacement()
        self._files = options.get_files()

        for file in self._files:
            if os.path.isfile(file):
                self._replace(file)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
