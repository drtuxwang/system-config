#!/usr/bin/env python3
"""
Make a compressed archive in 7Z format.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        if os.name == 'nt':
            self._archiver = syslib.Command('7z.dll', check=False)
        else:
            self._archiver = syslib.Command('7z.so', check=False)
        if self._archiver.is_found():
            self._archiver = syslib.Command('7z')
        else:
            self._archiver = syslib.Command('7za')

        if len(args) > 1 and args[1] in ('a', '-bd', 'l', 't', 'x'):
            self._archiver.set_args(args[1:])
            self._archiver.run(mode='exec')

        self._parse_args(args[1:])

        if self._args.split:
            self._archiver.extend_flags(['-v' + str(self._args.split[0]) + 'b'])

        if self._args.threads[0] == '1':
            self._archiver.set_flags(
                ['a', '-m0=lzma', '-mmt=' + str(self._args.threads[0]), '-mx=9', '-ms=on', '-y'])
        else:
            self._archiver.set_flags(
                ['a', '-m0=lzma2', '-mmt=' + str(self._args.threads[0]), '-mx=9', '-ms=on', '-y'])

        if os.path.isdir(self._args.archive[0]):
            self._archiver.set_args([os.path.abspath(self._args.archive[0]) + '.7z'])
        else:
            self._archiver.set_args(self._args.archive)

        if self._args.files:
            self._archiver.extend_args(self._args.files)
        else:
            self._archiver.extend_args(os.listdir())

        self._setenv()

    def get_archiver(self):
        """
        Return archiver Command class object.
        """
        return self._archiver

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Make a compressed archive in 7z format.')

        parser.add_argument('-split', nargs=1, type=int, metavar='bytes',
                            help='Split archive into chucks with selected size.')
        parser.add_argument('-threads', nargs=1, type=int, default=[2],
                            help='Threads are faster but decrease quality. Default is 2.')
        parser.add_argument('archive', nargs=1, metavar='file.7z|file.bin|file.exe|directory',
                            help='Archive file or directory.')
        parser.add_argument('files', nargs='*', metavar='file',
                            help='File or directory.')

        self._args = parser.parse_args(args)

        if self._args.split and self._args.split[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for split size.')
        if self._args.threads[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                             'number of threads.')

    def _setenv(self):
        if 'LANG' in os.environ:
            del os.environ['LANG']  # Avoids locale problems


class Pack(object):
    """
    Pack class
    """

    def __init__(self, options):
        os.umask(int('022', 8))
        archiver = options.get_archiver()

        archive = archiver.get_args()[0]
        sfx = self._check_sfx(archiver, archive)

        archiver.run()
        if archiver.get_exitcode():
            print(sys.argv[0] + ': Error code ' + str(archiver.get_exitcode()) +
                  ' received from "' + archiver.get_file() + '".', file=sys.stderr)
            raise SystemExit(archiver.get_exitcode())
        if sfx:
            self._make_sfx(archive, sfx)

    def _check_sfx(self, archiver, archive):
        sfx = ''
        file = os.path.basename(archive)
        if '.bin' in file or '.exe' in file:
            sfx = os.path.join(os.path.dirname(archiver.get_file()), '7zCon.sfx')
            if '.exe' in file and syslib.info.get_system() != 'windows':
                sfx = os.path.join(os.path.dirname(archiver.get_file()), '7zCon.exe')
            if not os.path.isfile(sfx):
                archiver = syslib.Command(archiver.get_program(), args=archiver.get_args(),
                                          check=False)
                if not archiver.is_found():
                    raise SystemExit(sys.argv[0] + ': Cannot find "' + sfx + '" SFX file.')
                archiver.run(mode='exec')
        return sfx

    def _make_sfx(self, archive, sfx):
        print('Adding SFX code')
        with open(archive + '-sfx', 'wb') as ofile:
            try:
                with open(sfx, 'rb') as ifile:
                    self._copy(ifile, ofile)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot read "' + sfx + '" SFX file.')
            with open(archive, 'rb') as ifile:
                self._copy(ifile, ofile)

        try:
            os.rename(archive + '-sfx', archive)
            os.chmod(archive, int('755', 8))
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot rename "' + archive +
                             '-sfx" file to "' + archive + '".')

    def _copy(self, ifile, ofile):
        while True:
            chunk = ifile.read(131072)
            if not chunk:
                break
            ofile.write(chunk)


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
            Pack(options)
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
