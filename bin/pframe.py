#!/usr/bin/env python3
"""
Resize/rotate picture images to fit digital photo frames.
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

        try:
            x, y = self._args.bsize[0].split(':')
            self._border_size_x = int(x)
            self._border_size_y = int(y)
            if self._border_size_x < 0 or self._border_size_y < 0:
                raise ValueError
        except ValueError:
            raise SystemExit(sys.argv[0] + ': Invalid border size "' + self._args.bsize[0] + '".')

        try:
            x, y = self._args.size[0].split(':')
            self._size_x = int(x)
            self._size_y = int(y)
            if self._size_x < 1 or self._size_y < 1:
                raise ValueError
        except ValueError:
            raise SystemExit(sys.argv[0] + ': Invalid image size "' + self._args.size[0] + '".')

        self._convert = syslib.Command('convert')

    def get_border_colour(self):
        """
        Return bcolour flag.
        """
        return self._args.bcolor[0]

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

    def get_border_size_x(self):
        """
        Return bsizeX.
        """
        return self._border_size_x

    def get_border_size_y(self):
        """
        Return bsizeY.
        """
        return self._border_size_y

    def get_size_x(self):
        """
        Return sizeX.
        """
        return self._size_x

    def get_size_y(self):
        """
        Return sizeY.
        """
        return self._size_y

    def get_rotate_flag(self):
        """
        Return rotate flag.
        """
        return self._args.rotateFlag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Resize/rotate picture images to fit digital photo frames.')

        parser.add_argument('-bcolor', nargs=1, default=['black'],
                            help='Select border colour. Default is black.')
        parser.add_argument('-bsize', nargs=1, default=['0:0'], metavar='x:y',
                            help='Select border size. Default 0:0.')
        parser.add_argument('-rotate', dest='rotateFlag', action='store_true',
                            help='Enable rotation image if needed. Default is no rotate.')
        parser.add_argument('-size', nargs=1, default=['1024:600'], metavar='x:y',
                            help='Select photo frame resolution. Default is 1024:600.')

        parser.add_argument('directories', nargs='+', metavar='directory',
                            help='Directory containing JPEG files to frame.')

        self._args = parser.parse_args(args)

        for directory in self._args.directories:
            if not os.path.isdir(directory):
                raise SystemExit(
                    sys.argv[0] + ': Image directory "' + directory + '" does not exist.')


class Frame(object):
    """
    Frame class
    """

    def __init__(self, options):
        self._convert = options.get_convert()
        bcolour = options.get_border_colour()
        bsizeX = options.get_border_size_x()
        bsizeY = options.get_border_size_y()
        sizeX = options.get_size_x()
        sizeY = options.get_size_y()
        rotateFlag = options.get_rotate_flag()

        x = sizeX - bsizeX
        y = sizeY - bsizeY
        if x < 0 or y < 0:
            raise SystemExit(sys.argv[0] + ': Border size cannot be bigger than frame resolution.')
        for directory in options.get_directories():
            for file in glob.glob(os.path.join(directory, '*')):
                if (file.split('.')[-1].lower() in (
                        'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pcx', 'svg', 'tif', 'tiff')):
                    if not os.path.isfile(file):
                        raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" picture file.')
                    ix, iy = self._imagesize(options, file)
                    sys.stdout.write(file + ': ' + str(ix) + 'x' + str(iy))
                    if ix != sizeX or iy != sizeY:
                        if rotateFlag:
                            if dfpx > dfpy:
                                if iy > ix:
                                    ix, iy = self._imagerotate(options, file)
                                    sys.stdout.write(' => Rotate (' + str(ix) + 'x' + str(iy) +
                                                     ')')
                            elif ix > iy:
                                ix, iy = self._imagerotate(options, file)
                                sys.stdout.write(' => Rotate (' + str(ix) + 'x' + str(iy) + ')')
                        if ix != x or iy != y:
                            self._convert.set_args([
                                '-verbose', '-size', str(x) + 'x' + str(y), '-resize',
                                str(x) + 'x' + str(y), file, file])
                            self._convert.run(mode='batch')
                            if self._convert.get_exitcode():
                                raise SystemExit(
                                    sys.argv[0] + ': Error code ' +
                                    str(self._convert.get_exitcode()) + ' received from "' +
                                    self._convert.get_file() + '".')
                            elif self._convert.get_exitcode():
                                raise SystemExit(
                                    sys.argv[0] + ': Error code ' +
                                    str(self._convert.get_exitcode()) + ' received from "' +
                                    self._convert.get_file() + '".')
                            ix, iy = self._imagesize(options, file)
                            sys.stdout.write(' => Resize (' + str(ix) + 'x' + str(iy) + ')')
                        bx = int((bsizeX + x - ix) / 2)
                        by = int((bsizeY + y - iy) / 2)
                        if bx or by:
                            self._convert.set_args([
                                '-verbose', '-size', str(x) + 'x' + str(y), '-bordercolor',
                                bcolour, '-border', str(bx) + 'x' + str(by), '-resize', str(sizeX) +
                                'x' + str(sizeY) + '!', file, file])
                            self._convert.run(mode='batch')
                            if self._convert.get_exitcode():
                                raise SystemExit(
                                    sys.argv[0] + ': Error code ' +
                                    str(self._convert.get_exitcode()) + ' received from "' +
                                    self._convert.get_file() + '".')
                            ix, iy = self._imagesize(options, file)
                            sys.stdout.write(' => Border (' + str(ix) + 'x' + str(iy) + ')')
                    print()

    def _imagerotate(self, options, file):
        self._convert.set_args(['-verbose', '-rotate', '270', file, file])
        self._convert.run(mode='batch')
        if self._convert.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._convert.get_exitcode()) +
                             ' received from "' + self._convert.get_file() + '".')
        return self._imagesize(options, file)

    def _imagesize(self, options, file):
        self._convert.set_args(['-verbose', file, '/dev/null'])
        self._convert.run(filter='^' + file + '=>', mode='batch', error2output=True)
        if not self._convert.has_output():
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" picture file.')
        elif self._convert.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._convert.get_exitcode()) +
                             ' received from "' + self._convert.get_file() + '".')
        x, y = self._convert.get_output()[0].split('+')[0].split()[-1].split('x')
        return (int(x), int(y))


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
            Frame(options)
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
