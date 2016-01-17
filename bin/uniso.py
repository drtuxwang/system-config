#!/usr/bin/env python3
"""
Unpack a portable CD/DVD archive in ISO9660 format.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(sys.argv[0] + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

    def get_images(self):
        """
        Return list of ISO images.
        """
        return self._args.images

    def get_view_flag(self):
        """
        Return view flag.
        """
        return self._args.viewFlag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Unpack a portable CD/DVD archive in ISO9660 format.')

        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='Show contents of archive.')

        parser.add_argument('images', nargs='+', metavar='image.iso', help='ISO image file.')

        self._args = parser.parse_args(args)


class Unpack(object):
    """
    Unpack class
    """

    def __init__(self, options):
        os.umask(int('022', 8))
        viewFlag = options.get_view_flag()

        if viewFlag:
            archiver = syslib.Command('7z', flags=['l'])
            isoinfo = syslib.Command('isoinfo', flags=['-d', '-i'])
        else:
            archiver = syslib.Command('7z', flags=['x', '-y'])

        for image in options.get_images():
            if not os.path.isfile(image):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + image + '" ISO9660 file.')
            archiver.set_args([image])
            archiver.run()
            if archiver.get_exitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(archiver.get_exitcode()) +
                                 ' received from "' + archiver.get_file() + '".')
            if viewFlag:
                isoinfo.set_args([image])
                isoinfo.run()
                if isoinfo.get_exitcode():
                    raise SystemExit(sys.argv[0] + ': Error code ' + str(isoinfo.get_exitcode()) +
                                     ' received from "' + isoinfo.get_file() + '".')
                self._isosize(image, syslib.FileStat(image).get_size())

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
