#!/usr/bin/env python3
"""
Make a compressed archive in TAR/TAR.GZ/TAR.BZ2/TAR.LZMA/TAR.XZ/TAR.7Z/TGZ/TBZ|TLZ|TXZ format.
"""

import argparse
import glob
import os
import re
import signal
import sys
import tarfile

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

    def get_archive(self):
        """
        Return archive location.
        """
        return self._archive

    def get_files(self):
        """
        Return list of files.
        """
        return self._files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Make a compressed archive in TAR format.')

        parser.add_argument('archive', nargs=1,
                            metavar='file.tar|file.tar.gz|file.tar.bz2|file.tar.lzma|file.tar.xz|'
                                    'file.tar.7z|file.tgz|file.tbz|file.tlz|file.txz',
                            help='Archive file.')
        parser.add_argument('files', nargs='*', metavar='file',
                            help='File or directory.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if os.path.isdir(self._args.archive[0]):
            self._archive = os.path.abspath(self._args.archive[0]) + '.tar'
        else:
            self._archive = self._args.archive[0]
        isarchive = re.compile('[.](tar|tar[.](gz|bz2|lzma|xz|7z)|t[gblx]z)$')
        if not isarchive.search(self._archive):
            raise SystemExit(sys.argv[0] + ': Unsupported "' + self._archive + '" archive format.')

        if self._args.files:
            self._files = self._args.files
        else:
            self._files = os.listdir()


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

    def _addfile(self, files):
        for file in sorted(files):
            print(file)
            try:
                self._archive.add(file, recursive=False)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot open "' + file + '" file.')
            if os.path.isdir(file) and not os.path.islink(file):
                try:
                    self._addfile([os.path.join(file, x) for x in os.listdir(file)])
                except PermissionError:
                    raise SystemExit(sys.argv[0] + ': Cannot open "' + file + '" directory.')

    def run(self):
        """
        Start program
        """
        options = Options()

        if options.get_archive().endswith('.tar'):
            try:
                self._archive = tarfile.open(options.get_archive(), 'w:')
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' +
                                 options.get_archive() + '" archive file.')
            self._addfile(options.get_files())
            self._archive.close()
        else:
            tar = command_mod.Command('tar', errors='stop')
            archive = options.get_archive()
            if archive.endswith('.tar.7z'):
                tar.set_args(['cf', '-'] + options.get_files())
                p7zip = command_mod.Command('7za', errors='stop')
                p7zip.set_args([
                    'a', '-m0=lzma2', '-mmt=2', '-mx=9', '-ms=on', '-y', '-si', archive])
                subtask_mod.Task(tar.get_cmdline() + ['|'] + p7zip.get_cmdline()).run()
            elif archive.endswith('.txz') or archive.endswith('.tar.xz'):
                tar.set_args(['cfvJ', archive] + options.get_files())
                os.environ['XZ_OPT'] = '-9 -e --lzma2=dict=128MiB'
                subtask_mod.Exec(tar.get_cmdline()).run()
            else:
                tar.set_args(['cfva', archive] + options.get_files())
                os.environ['GZIP'] = '-9'
                os.environ['BZIP2'] = '-9'
                os.environ['XZ_OPT'] = '-9 -e --lzma2=dict=128MiB'
                subtask_mod.Exec(tar.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
