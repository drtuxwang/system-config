#!/usr/bin/env python3
"""
Re-format Javascript file.
"""

import argparse
import glob
import os
import shutil
import signal
import sys

import jsbeautifier


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

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Re-format Javascript file.')

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='File to change.'
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
    def run():
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" file.')
            print('Re-formatting "' + file + '" XML file...')

            lines = []
            try:
                with open(file, errors='replace') as ifile:
                    for line in ifile:
                        lines.append(line.strip())
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot read "' + file + '" file.')

            tmpfile = file + '-tmp' + str(os.getpid())
            try:
                with open(tmpfile, 'w', newline='\n') as ofile:
                    print(jsbeautifier.beautify(''.join(lines)), file=ofile)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + tmpfile + '" file.')
            try:
                shutil.move(tmpfile, file)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot rename "' + tmpfile +
                    '" file to "' + file + '".'
                )


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
