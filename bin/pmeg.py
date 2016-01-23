#!/usr/bin/env python3
"""
Resize large picture images to mega-pixels limit.
"""

import argparse
import glob
import math
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

        self._convert = syslib.Command('convert')

    def get_convert(self):
        """
        Return convert Command class object.
        """
        return self._convert

    def get_directories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def get_megs(self):
        """
        Return mega-pixels.
        """
        return self._args.megs[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Resize large picture images to mega-pixels limit.')

        parser.add_argument('-megs', nargs=1, type=float, default=[9],
                            help='Select mega-pixels. Default is 9.')

        parser.add_argument('directories', nargs='+', metavar='directory',
                            help='Directory containing JPEG files to resize.')

        self._args = parser.parse_args(args)

        if self._args.megs[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive number for megabytes.')

        for directory in self._args.directories:
            if not os.path.isdir(directory):
                raise SystemExit(
                    sys.argv[0] + ': Image directory "' + directory + '" does not exist.')


class Remeg(object):
    """
    Change metai-pixels class
    """

    def __init__(self, options):
        self._convert = options.get_convert()
        megs = options.get_megs()

        for directory in options.get_directories():
            for file in sorted(glob.glob(os.path.join(directory, '*'))):
                if (file.split('.')[-1].lower() in (
                        'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pcx', 'svg', 'tif', 'tiff')):
                    ix_size, iy_size = self._imagesize(file)
                    imegs = ix_size * iy_size / 1000000
                    print('{0:s}: {1:d} x {2:d} ({3:4.2f})'.format(
                        file, ix_size, iy_size, imegs), end='')
                    resize = math.sqrt(megs / imegs)
                    ox_size = int(ix_size*resize + 0.5)
                    oy_size = int(iy_size*resize + 0.5)
                    if ox_size < ix_size and oy_size < iy_size:
                        print(' => {0:d} x {1:d} ({2:4.2f})'.format(
                            ox_size, oy_size, ox_size * oy_size / 1000000), end='')
                        self._convert.set_args(
                            ['-verbose', '-size', str(ox_size) + 'x' + str(oy_size),
                             '-resize', str(ox_size) + 'x' + str(oy_size) + '!', file, file])
                        self._convert.run(mode='batch')
                        if self._convert.get_exitcode():
                            raise SystemExit(
                                sys.argv[0] + ': Error code ' + str(self._convert.get_exitcode()) +
                                ' received from "' + self._convert.get_file() + '".')
                    print()

    def _imagesize(self, file):
        self._convert.set_args(['-verbose', file, '/dev/null'])
        self._convert.run(filter='^' + file + '=>', mode='batch', error2output=True)
        if not self._convert.has_output():
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" picture file.')
        elif self._convert.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._convert.get_exitcode()) +
                             ' received from "' + self._convert.get_file() + '".')
        x_size, y_size = self._convert.get_output()[0].split('+')[0].split()[-1].split('x')
        return (int(x_size), int(y_size))


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
            Remeg(options)
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
