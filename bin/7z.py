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

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options:

    def __init__(self, args):
        if os.name == 'nt':
            self._archiver = syslib.Command('7z.dll', check=False)
        else:
            self._archiver = syslib.Command('7z.so', check=False)
        if self._archiver.isFound():
            self._archiver = syslib.Command('7z')
        else:
            self._archiver = syslib.Command('7za')

        if len(args) > 1 and args[1] in ('a', '-bd', 'l', 't', 'x'):
            self._archiver.setArgs(args[1:])
            self._archiver.run(mode='exec')

        self._parseArgs(args[1:])

        if self._args.split:
            self._archiver.extendFlags(['-v' + str(self._args.split[0]) + 'b'])

        if self._args.threads[0] == '1':
            self._archiver.setFlags(['a', '-m0=lzma', '-mmt=' + str(self._args.threads[0]),
                                     '-mx=9', '-ms=on', '-y'])
        else:
            self._archiver.setFlags(['a', '-m0=lzma2', '-mmt=' + str(self._args.threads[0]),
                                     '-mx=9', '-ms=on', '-y'])

        if os.path.isdir(self._args.archive[0]):
            self._archiver.setArgs([os.path.abspath(self._args.archive[0]) + '.7z'])
        else:
            self._archiver.setArgs(self._args.archive)

        if self._args.files:
            self._archiver.extendArgs(self._args.files)
        else:
            self._archiver.extendArgs(os.listdir())

        self._setenv()

    def getArchiver(self):
        """
        Return archiver Command class object.
        """
        return self._archiver

    def _parseArgs(self, args):
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


class Pack:

    def __init__(self, options):
        os.umask(int('022', 8))
        archiver = options.getArchiver()

        archive = archiver.getArgs()[0]
        sfx = self._checkSfx(archiver, archive)

        archiver.run()
        if archiver.getExitcode():
            print(sys.argv[0] + ': Error code ' + str(archiver.getExitcode()) + ' received from "' +
                  archiver.getFile() + '".', file=sys.stderr)
            raise SystemExit(archiver.getExitcode())
        if sfx:
            self._makeSfx(archive, sfx)

    def _checkSfx(self, archiver, archive):
        sfx = ''
        file = os.path.basename(archive)
        if '.bin' in file or '.exe' in file:
            sfx = os.path.join(os.path.dirname(archiver.getFile()), '7zCon.sfx')
            if '.exe' in file and syslib.info.getSystem() != 'windows':
                sfx = os.path.join(os.path.dirname(archiver.getFile()), '7zCon.exe')
            if not os.path.isfile(sfx):
                archiver = syslib.Command(archiver.getProgram(), args=archiver.getArgs(),
                                          check=False)
                if not archiver.isFound():
                    raise SystemExit(sys.argv[0] + ': Cannot find "' + sfx + '" SFX file.')
                archiver.run(mode='exec')
        return sfx

    def _makeSfx(self, archive, sfx):
        print('Adding SFX code')
        with open(archive + '-sfx', 'wb') as ofile:
            try:
                with open(sfx, 'rb') as ifile:
                    self._copy(ifile, ofile)
            except IOError:
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


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
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
