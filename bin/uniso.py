#!/usr/bin/env python3
"""
Unpack a portable CD/DVD archive in ISO9660 format.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import re
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getImages(self):
        """
        Return list of ISO images.
        """
        return self._args.images

    def getViewFlag(self):
        """
        Return view flag.
        """
        return self._args.viewFlag

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Unpack a portable CD/DVD archive in ISO9660 format.')

        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='Show contents of archive.')

        parser.add_argument('images', nargs='+', metavar='image.iso', help='ISO image file.')

        self._args = parser.parse_args(args)


class Unpack(syslib.Dump):

    def __init__(self, options):
        os.umask(int('022', 8))
        viewFlag = options.getViewFlag()

        if viewFlag:
            archiver = syslib.Command('7z', flags=['l'])
            isoinfo = syslib.Command('isoinfo', flags=['-d', '-i'])
        else:
            archiver = syslib.Command('7z', flags=['x', '-y'])

        for image in options.getImages():
            if not os.path.isfile(image):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + image + '" ISO9660 file.')
            archiver.setArgs([image])
            archiver.run()
            if archiver.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(archiver.getExitcode()) +
                                 ' received from "' + archiver.getFile() + '".')
            if viewFlag:
                isoinfo.setArgs([image])
                isoinfo.run()
                if isoinfo.getExitcode():
                    raise SystemExit(sys.argv[0] + ': Error code ' + str(isoinfo.getExitcode()) +
                                     ' received from "' + isoinfo.getFile() + '".')
                self._isosize(image, syslib.FileStat(image).getSize())

    def _isosize(self, image, size):
        if size > 734003200:
            print('\n*** {0:s}: {1:4.2f} MB ({2:5.3f} salesman"s GB) ***\n'.format(
                  image, size/1048576., size/1000000000.))
            if size > 9400000000:
                sys.stderr.write('**WARNING** This ISO image file does not fit onto '
                                 '9.4GB/240min Duel Layer DVD media.\n')
                sys.stderr.write('        ==> Please split your data into multiple images.\n')
            elif size > 4700000000:
                sys.stderr.write('**WARNING** This ISO image file does not fit onto '
                                 '4.7GB/120min DVD media.\n')
                sys.stderr.write('        ==> Please use Duel Layer DVD media or split your '
                                 ' data into multiple images.\n')
            else:
                sys.stderr.write('**WARNING** This ISO image file does not fit onto '
                                 '700MB/80min CD media.\n')
                sys.stderr.write('        ==> Please use DVD media or split your '
                                 'data into multiple images.\n')
            print('')
        else:
            minutes, remainder = divmod(size, 734003200 / 80)
            seconds = remainder * 4800 / 734003200.
            print('\n*** {0:s}: {1:4.2f} MB ({2:.0f} min {3:05.2f} sec) ***\n'.format(
                  image, size/1048576., minutes, seconds))
            if size > 681574400:
                sys.stderr.write('**WARNING** This ISO image file does not fit onto '
                                 '650MB/74min CD media.\n')
                sys.stderr.write('        ==> Please use 700MB/80min CD media instead.\n')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
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
