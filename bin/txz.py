#!/usr/bin/env python3
"""
Make a compressed archive in TAR.XZ format.
"""

import argparse
import glob
import os
import shutil
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


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

    def get_tar(self):
        """
        Return tar Command class object.
        """
        return self._tar

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Make a compressed archive in TAR.XZ format.')

        parser.add_argument(
            'archive',
            nargs=1,
            metavar='file.tar.xz|file.txz',
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
            self._archive = os.path.abspath(self._args.archive[0]) + '.tar.xz'
        else:
            self._archive = self._args.archive[0]
        if not self._archive.endswith(('.tar.xz', '.txz')):
            raise SystemExit(
                sys.argv[0] + ': Unsupported "' + self._archive +
                '" archive format.'
            )

        if self._args.files:
            self._files = self._args.files
        else:
            self._files = os.listdir()

        self._tar = command_mod.Command('tar', errors='stop')
        self._tar.set_args(['cfvJ', self._archive+'.part'] + self._files)

        os.environ['XZ_OPT'] = '-9 -e --lzma2=dict=128MiB --threads=1'


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
        archive = options.get_archive()

        os.umask(int('022', 8))

        task = subtask_mod.Task(options.get_tar().get_cmdline())
        task.run()
        try:
            if task.get_exitcode():
                raise OSError
            shutil.move(archive+'.part', archive)
        except OSError:
            raise SystemExit(
                '{0:s}: Cannot create "{1:s}" archive file.'.format(
                    sys.argv[0],
                    archive
                )
            )


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
