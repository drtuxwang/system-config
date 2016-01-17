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

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        self._gs = syslib.Command('gs')
        self._gs.set_flags(
            ['-dNOPAUSE', '-dBATCH', '-dSAFER', '-sDEVICE=jpeg', '-r' + str(self._args.dpi[0])])

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


class Unpack(object):
    """
    Unpack class
    """

    def __init__(self, options):
        gs = options.get_gs()

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
            gs.set_args(['-sOutputFile=' + directory + os.sep + '%08d.jpg', '-c',
                         'save', 'pop', '-f', file])
            gs.run(filter='Ghostscript|^Copyright|WARRANTY:|^Processing')
            if gs.get_exitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(gs.get_exitcode()) +
                                 ' received from "' + gs.get_file() + '".')


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
            Unpack(options)
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
