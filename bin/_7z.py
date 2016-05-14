#!/usr/bin/env python3
"""
Make a compressed archive in 7Z format.
"""

import argparse
import glob
import os
import shutil
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_archiver(self):
        """
        Return archiver Command class object.
        """
        return self._archiver

    def get_archive(self):
        """
        Return archive file.
        """
        return self._archive

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

    @staticmethod
    def _setenv():
        if 'LANG' in os.environ:
            del os.environ['LANG']  # Avoids locale problems

    def parse(self, args):
        """
        Parse arguments
        """
        if os.name == 'nt':
            self._archiver = command_mod.Command('7z.dll', errors='ignore')
        else:
            self._archiver = command_mod.Command('7z.so', errors='ignore')
        if self._archiver.is_found():
            self._archiver = command_mod.Command('7z')
        else:
            self._archiver = command_mod.Command('7za')

        if len(args) > 1 and args[1] in ('a', '-bd', 'l', 't', 'x'):
            self._archiver.set_args(args[1:])
            subtask_mod.Exec(self._archiver.get_cmdline()).run()

        self._parse_args(args[1:])

        if self._args.split:
            self._archiver.extend_args(['-v' + str(self._args.split[0]) + 'b'])

        if self._args.threads[0] == '1':
            self._archiver.set_args(
                ['a', '-m0=lzma', '-mmt=' + str(self._args.threads[0]), '-mx=9', '-ms=on', '-y'])
        else:
            self._archiver.set_args(
                ['a', '-m0=lzma2', '-mmt=' + str(self._args.threads[0]), '-mx=9', '-ms=on', '-y'])

        if os.path.isdir(self._args.archive[0]):
            self._archive = os.path.abspath(self._args.archive[0]) + '.7z'
        else:
            self._archive = self._args.archive[0]
        self._archiver.extend_args([self._archive])

        if self._args.files:
            self._archiver.extend_args(self._args.files)
        else:
            self._archiver.extend_args(os.listdir())

        self._setenv()


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
    def _check_sfx(archiver, archive):
        file = os.path.basename(archive)
        if file.endswith('.bin'):
            sfx = os.path.join(os.path.dirname(archiver.get_file()), '7zCon.sfx')
        elif file.endswith('.exe'):
            sfx = os.path.join(os.path.dirname(archiver.get_file()), '7zExe.sfx')
        else:
            return ''

        if not os.path.isfile(sfx):
            raise SystemExit(sys.argv[0] + ': Cannot find "' + sfx + '" SFX file.')
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
            os.chmod(archive + '-sfx', int('755', 8))
            shutil.move(archive + '-sfx', archive)
        except OSError:
            raise SystemExit(sys.argv[0] + ': Cannot rename "' + archive +
                             '-sfx" file to "' + archive + '".')

    @staticmethod
    def _copy(ifile, ofile):
        while True:
            chunk = ifile.read(131072)
            if not chunk:
                break
            ofile.write(chunk)

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

    def run(self):
        """
        Start program
        """
        os.umask(int('022', 8))

        options = Options()
        archiver = options.get_archiver()
        archive = options.get_archive()
        sfx = self._check_sfx(archiver, archive)

        task = subtask_mod.Task(archiver.get_cmdline())
        task.run()
        if task.get_exitcode():
            print(sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                  ' received from "' + task.get_file() + '".', file=sys.stderr)
            raise SystemExit(task.get_exitcode())

        if sfx:
            self._make_sfx(archive, sfx)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
