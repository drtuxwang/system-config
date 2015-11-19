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


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

        try:
            x, y = self._args.bsize[0].split(':')
            self._bsizeX = int(x)
            self._bsizeY = int(y)
            if self._bsizeX < 0 or self._bsizeY < 0:
                raise ValueError
        except ValueError:
            raise SystemExit(sys.argv[0] + ': Invalid border size "' + self._args.bsize[0] + '".')

        try:
            x, y = self._args.size[0].split(':')
            self._sizeX = int(x)
            self._sizeY = int(y)
            if self._sizeX < 1 or self._sizeY < 1:
                raise ValueError
        except ValueError:
            raise SystemExit(sys.argv[0] + ': Invalid image size "' + self._args.size[0] + '".')

        self._convert = syslib.Command('convert')

    def getBcolour(self):
        """
        Return bcolour flag.
        """
        return self._args.bcolor[0]

    def getConvert(self):
        """
        Return convert Command class object.
        """
        return self._convert

    def getDirectorys(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def getBsizeX(self):
        """
        Return bsizeX.
        """
        return self._bsizeX

    def getBsizeY(self):
        """
        Return bsizeY.
        """
        return self._bsizeY

    def getSizeX(self):
        """
        Return sizeX.
        """
        return self._sizeX

    def getSizeY(self):
        """
        Return sizeY.
        """
        return self._sizeY

    def getRotateFlag(self):
        """
        Return rotate flag.
        """
        return self._args.rotateFlag

    def _parseArgs(self, args):
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


class Frame:

    def __init__(self, options):
        self._convert = options.getConvert()
        bcolour = options.getBcolour()
        bsizeX = options.getBsizeX()
        bsizeY = options.getBsizeY()
        sizeX = options.getSizeX()
        sizeY = options.getSizeY()
        rotateFlag = options.getRotateFlag()

        x = sizeX - bsizeX
        y = sizeY - bsizeY
        if x < 0 or y < 0:
            raise SystemExit(sys.argv[0] + ': Border size cannot be bigger than frame resolution.')
        for directory in options.getDirectorys():
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
                            self._convert.setArgs([
                                '-verbose', '-size', str(x) + 'x' + str(y), '-resize',
                                str(x) + 'x' + str(y), file, file])
                            self._convert.run(mode='batch')
                            if self._convert.getExitcode():
                                raise SystemExit(
                                    sys.argv[0] + ': Error code ' +
                                    str(self._convert.getExitcode()) + ' received from "' +
                                    self._convert.getFile() + '".')
                            elif self._convert.getExitcode():
                                raise SystemExit(
                                    sys.argv[0] + ': Error code ' +
                                    str(self._convert.getExitcode()) + ' received from "' +
                                    self._convert.getFile() + '".')
                            ix, iy = self._imagesize(options, file)
                            sys.stdout.write(' => Resize (' + str(ix) + 'x' + str(iy) + ')')
                        bx = int((bsizeX + x - ix) / 2)
                        by = int((bsizeY + y - iy) / 2)
                        if bx or by:
                            self._convert.setArgs([
                                '-verbose', '-size', str(x) + 'x' + str(y), '-bordercolor',
                                bcolour, '-border', str(bx) + 'x' + str(by), '-resize', str(sizeX) +
                                'x' + str(sizeY) + '!', file, file])
                            self._convert.run(mode='batch')
                            if self._convert.getExitcode():
                                raise SystemExit(
                                    sys.argv[0] + ': Error code ' +
                                    str(self._convert.getExitcode()) + ' received from "' +
                                    self._convert.getFile() + '".')
                            ix, iy = self._imagesize(options, file)
                            sys.stdout.write(' => Border (' + str(ix) + 'x' + str(iy) + ')')
                    print()

    def _imagerotate(self, options, file):
        self._convert.setArgs(['-verbose', '-rotate', '270', file, file])
        self._convert.run(mode='batch')
        if self._convert.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._convert.getExitcode()) +
                             ' received from "' + self._convert.getFile() + '".')
        return self._imagesize(options, file)

    def _imagesize(self, options, file):
        self._convert.setArgs(['-verbose', file, '/dev/null'])
        self._convert.run(filter='^' + file + '=>', mode='batch', error2output=True)
        if not self._convert.hasOutput():
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" picture file.')
        elif self._convert.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._convert.getExitcode()) +
                             ' received from "' + self._convert.getFile() + '".')
        x, y = self._convert.getOutput()[0].split('+')[0].split()[-1].split('x')
        return (int(x), int(y))


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
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
