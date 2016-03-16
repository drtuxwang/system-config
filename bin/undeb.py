#!/usr/bin/env python3
"""
Unpack a compressed archive in DEB format.
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

    def get_archives(self):
        """
        Return list of archives.
        """
        return self._args.archives

    def get_view_flag(self):
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Unpack a compressed archive in DEB format.')

        parser.add_argument('-v', dest='view_flag', action='store_true',
                            help='Show contents of archive.')

        parser.add_argument('archives', nargs='+', metavar='file.deb', help='Archive file.')

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
    def _remove(*files):
        for file in files:
            try:
                os.remove(file)
            except OSError:
                pass

    def _unpack(self, file):
        self._ar.set_args(['tv', file])
        self._ar.run(filter='data.tar', mode='batch')
        if len(self._ar.get_output()) != 1:
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" DEB file.')
        elif self._ar.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._ar.get_exitcode()) +
                             ' received from "' + self._ar.get_file() + '".')
        archive = self._ar.get_output()[-1].split()[-1]
        self._remove(archive, 'data.tar')
        self._ar.set_args(['x', file, archive])
        self._ar.run()
        if self._ar.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._ar.get_exitcode()) +
                             ' received from "' + self._ar.get_file() + '".')
        self._p7zip.set_args([archive])
        self._p7zip.run(mode='batch')
        if self._p7zip.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._p7zip.get_exitcode()) +
                             ' received from "' + self._p7zip.get_file() + '".')
        self._tar.set_args(['data.tar'])
        self._tar.run()
        if self._tar.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._tar.get_exitcode()) +
                             ' received from "' + self._tar.get_file() + '".')
        self._remove(archive, 'data.tar')
        self._ar.set_args(['x', file, 'control.tar.gz'])
        self._ar.run()
        if self._ar.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._ar.get_exitcode()) +
                             ' received from "' + self._ar.get_file() + '".')
        if not self._options.get_view_flag() and not os.path.isdir('DEBIAN'):
            try:
                os.mkdir('DEBIAN')
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot create "DEBIAN" directory.')
        if os.path.isdir('DEBIAN'):
            self._tar.set_args([os.path.join(os.pardir, 'control.tar.gz')])
            self._tar.run(directory='DEBIAN', replace=(os.curdir, 'DEBIAN'))
        else:
            self._tar.set_args(['control.tar.gz'])
            self._tar.run(replace=(os.curdir, 'DEBIAN'))
        if self._tar.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(self._tar.get_exitcode()) +
                             ' received from "' + self._tar.get_file() + '".')
        self._remove('control.tar.gz')

    def run(self):
        """
        Start program
        """
        options = Options()

        os.umask(int('022', 8))
        self._options = options
        self._ar = syslib.Command('ar')
        self._p7zip = syslib.Command('7za', flags=['x'])
        if options.get_view_flag():
            self._tar = syslib.Command('tar', flags=['tf'])
        else:
            self._tar = syslib.Command('tar', flags=['xvf'])
        for file in options.get_archives():
            if not os.path.isfile(file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + file + '" DEB file.')
            self._unpack(file)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
