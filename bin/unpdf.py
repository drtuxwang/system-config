#!/usr/bin/env python3
"""
Unpack PDF file into series of JPG files.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


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

    def get_gs(self):
        """
        Return gs Command class object.
        """
        return self._gs

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Unpack PDF file into series of JPG files.')

        parser.add_argument('-dpi', nargs=1, type=int, default=[300],
                            help='Selects DPI resolution (default is 300).')

        parser.add_argument('files', nargs='+', metavar='file.pdf', help='PDF document file.')

        self._args = parser.parse_args(args)

        if self._args.dpi[0] < 50:
            raise SystemExit(sys.argv[0] + ': DPI resolution must be at least 50.')

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._gs = syslib.Command('gs')
        self._gs.set_flags(
            ['-dNOPAUSE', '-dBATCH', '-dSAFER', '-sDEVICE=jpeg', '-r' + str(self._args.dpi[0])])


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
        except (syslib.SyslibError, SystemExit) as exception:
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

        command = options.get_gs()

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" PDF file.')
            directory = file[:-4]
            if not os.path.isdir(directory):
                try:
                    os.mkdir(directory)
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + directory + '" directory.')
            print('Unpacking "' + directory + os.sep + '*.jpg" file...')
            command.set_args(['-sOutputFile=' + directory + os.sep + '%08d.jpg', '-c',
                              'save', 'pop', '-f', file])
            command.run(filter='Ghostscript|^Copyright|WARRANTY:|^Processing')
            if command.get_exitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(command.get_exitcode()) +
                                 ' received from "' + command.get_file() + '".')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
