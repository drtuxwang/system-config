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


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getFiles(self):
        """
        Return list of files.
        """
        return self._args.files

    def getPattern(self):
        """
        Return regular expression pattern.
        """
        return self._args.pattern[0]

    def getReplacement(self):
        """
        Return replacement.
        """
        return self._args.replacement[0]

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Replace contents of multiple files.')

        parser.add_argument('pattern', nargs=1, help='Regular expression.')
        parser.add_argument('replacement', nargs=1, help='Replacement for matches.')
        parser.add_argument('files', nargs='+', metavar='file', help='File or directory.')

        self._args = parser.parse_args(args)


class Replace:

    def __init__(self, options):
        try:
            self._isMatch = re.compile(options.getPattern())
        except re.error:
            raise SystemExit(
                sys.argv[0] + ': Invalid regular expression "' + options.getPattern() + '".')

        self._replacement = options.getReplacement()
        self._files = options.getFiles()

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
                            lineNew = self._isMatch.sub(self._replacement, line)
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


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
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
