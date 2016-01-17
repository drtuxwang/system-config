#!/usr/bin/env python3
"""
Replace contents of multiple files.
"""

import argparse
import glob
import os
import re
import signal
import sys

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

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
            description='Replace contents of multiple files.')

        parser.add_argument('pattern', nargs=1, help='Regular expression.')
        parser.add_argument('replacement', nargs=1, help='Replacement for matches.')
        parser.add_argument('files', nargs='+', metavar='file', help='File or directory.')

        self._args = parser.parse_args(args)


class Replace(object):
    """
    Replace class
    """

    def __init__(self, options):
        try:
            self._is_match = re.compile(options.get_pattern())
        except re.error:
            raise SystemExit(
                sys.argv[0] + ': Invalid regular expression "' + options.get_pattern() + '".')

        self._replacement = options.get_replacement()
        self._files = options.get_files()

    def run(self):
        for file in self._files:
            if os.path.isfile(file):
                self._replace(file)

    def _remove(self, *files):
        for file in files:
            try:
                os.remove(file)
            except OSError:
                pass

    def _replace(self, file):
        newfile = file + '-new'
        nchange = 0

        try:
            with open(file, errors='replace') as ifile:
                try:
                    with open(newfile, 'w', newline='\n') as ofile:
                        for line in ifile:
                            lineNew = self._is_match.sub(self._replacement, line)
                            print(lineNew, end='', file=ofile)
                            if lineNew != line:
                                nchange += 1
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + newfile + '" file.')
        except IOError:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')

        if nchange:
            if nchange > 1:
                print(newfile + ':', nchange, 'lines changed.')
            else:
                print(newfile + ':', nchange, 'line changed.')

            try:
                os.rename(newfile, file)
            except OSError:
                self._remove(newfile)
                raise SystemExit(sys.argv[0] + ': Cannot update "' + file + '" file.')
        else:
            self._remove(newfile)


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
            Replace(options).run()
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
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
