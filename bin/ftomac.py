#!/usr/bin/env python3
"""
Converts file to '\r' newline format.
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

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Converts file to "\\r" newline format.')

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
    def run():
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" file.')
            print(
                'Converting "' + file + '" file to "\\r" newline format...')
            try:
                with open(file, errors='replace') as ifile:
                    tmpfile = file + '-tmp' + str(os.getpid())
                    try:
                        with open(tmpfile, 'w', newline='\r') as ofile:
                            for line in ifile:
                                print(line.rstrip('\r\n'), file=ofile)
                    except OSError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create "' +
                            tmpfile + '" file.'
                        )
                    except UnicodeDecodeError:
                        os.remove(tmpfile)
                        raise SystemExit(
                            sys.argv[0] + ': Cannot convert "' + file +
                            '" binary file.'
                        )
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot read "' + file + '" file.')
            try:
                shutil.move(tmpfile, file)
            except OSError:
                os.remove(tmpfile)
                raise SystemExit(
                    sys.argv[0] + ': Cannot update "' + file + '" file.')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
