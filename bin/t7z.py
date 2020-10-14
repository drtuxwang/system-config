#!/usr/bin/env python3
"""
Make a compressed archive in TAR.7Z format.
"""

import argparse
import glob
import os
import shutil
import signal
import sys

import command_mod
import subtask_mod


class Options:
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
        parser = argparse.ArgumentParser(
            description='Make a compressed archive in TAR format.')

        parser.add_argument(
            'archive',
            nargs=1,
            metavar='file.tar.7z|file.t7z',
            help='Archive file.'
        )
        parser.add_argument(
            'files',
            nargs='*',
            metavar='file',
            help='File or directory.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if os.path.isdir(self._args.archive[0]):
            self._archive = os.path.abspath(self._args.archive[0]) + '.tar.7z'
        else:
            self._archive = self._args.archive[0]
        if not self._archive.endswith(('.tar.7z', '.t7z')):
            raise SystemExit(
                sys.argv[0] + ': Unsupported "' + self._archive +
                '" archive format.'
            )

        if self._args.files:
            self._files = self._args.files
        else:
            self._files = os.listdir()


class Main:
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
    def run():
        """
        Start program
        """
        options = Options()

        os.umask(int('022', 8))
        tar = command_mod.Command('tar', errors='stop')
        archive = options.get_archive()
        tar.set_args(['cf', '-'] + options.get_files())
        p7zip = command_mod.Command('7z', errors='stop')
        p7zip.set_args([
            'a',
            '-m0=lzma2',
            '-mmt=2',
            '-mx=9',
            '-ms=on',
            '-y',
            '-si',
            archive+'.part'
        ])
        task = subtask_mod.Task(
            tar.get_cmdline() + ['|'] + p7zip.get_cmdline()
        )

        task.run()
        try:
            if task.get_exitcode():
                raise OSError
            shutil.move(archive+'.part', archive)
        except OSError as exception:
            raise SystemExit(
                '{0:s}: Cannot create "{1:s}" archive file.'.format(
                    sys.argv[0],
                    archive
                )
            ) from exception


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
