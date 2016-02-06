#!/usr/bin/env python3
"""
Unpack a compressed archive in TAR/TAR.GZ/TAR.BZ2/TAR.LZMA/TAR.XZ/TAR.7Z/TGZ/TBZ/TLZ/TXZ format.
"""

import argparse
import glob
import os
import re
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

    def get_archives(self):
        """
        Return list of archives.
        """
        return self._args.archives

    def get_view_flag(self):
        """
        Return view flag.
        """
        return self._args.viewFlag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Unpack a compressed archive in '
                        'TAR/TAR.GZ/TAR.BZ2/TAR.LZMA/TAR.XZ/TAR.7Z/TGZ/TBZ/TLZ/TXZ format.')

        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='Show contents of archive.')

        parser.add_argument('archives', nargs='+',
                            metavar='file.tar|file.tar.gz|file.tar.bz2|file.tar.lzma|file.tar.xz|'
                                    'file.tar.7z|file.tgz|file.tbz|file.tlz|file.txz',
                            help='Archive file.')

        self._args = parser.parse_args(args)

        isarchive = re.compile('[.](tar|tar[.](gz|bz2|lzma|xz|7z)|t[gblx]z)$')
        for archive in self._args.archives:
            if not isarchive.search(archive):
                raise SystemExit(sys.argv[0] + ': Unsupported "' + archive + '" archive format.')

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

    def _unpack(self, archive):
        if archive.endswith('.tar.7z'):
            p7zip = syslib.Command('7za')
            p7zip.set_args(['x', '-y', '-so', archive])
            self._tar.set_args(['xfv', '-'])
            p7zip.run(pipes=[self._tar])
        else:
            self._tar.set_args(['xfv', archive])
            self._tar.run()

    def _view(self, archive):
        if archive.endswith('.tar.7z'):
            p7zip = syslib.Command('7za')
            p7zip.set_args(['x', '-y', '-so', archive])
            self._tar.set_args(['tfv', '-'])
            p7zip.run(pipes=[self._tar])
        else:
            self._tar.set_args(['tfv', archive])
            self._tar.run()

    def run(self):
        """
        Start program
        """
        options = Options()

        os.umask(int('022', 8))
        if os.name == 'nt':
            self._tar = syslib.Command('tar.exe')
        else:
            self._tar = syslib.Command('tar')
        for archive in options.get_archives():
            print(archive + ':')
            if options.get_view_flag():
                self._view(archive)
            else:
                self._unpack(archive)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
