#!/usr/bin/env python3
"""
Substitute patterns on lines in files.
"""

import argparse
import glob
import os
import re
import shutil
import signal
import sys

import file_mod


class Options:
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
            description='Substitute patterns on lines in files.')

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


class Main:
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
        newfile = file + '.part'
        nchange = 0

        try:
            with open(file, errors='replace') as ifile:
                try:
                    with open(newfile, 'w', newline='\n') as ofile:
                        for line in ifile:
                            line_new = self._is_match.sub(
                                self._replacement, line)
                            print(line_new, end='', file=ofile)
                            if line_new != line:
                                nchange += 1
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot create "' + newfile + '" file.'
                    )
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" file.')

        if nchange:
            if nchange > 1:
                print(file + ':', nchange, 'lines changed.')
            else:
                print(file + ':', nchange, 'line changed.')

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
