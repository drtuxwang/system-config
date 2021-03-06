#!/usr/bin/env python3
"""
Make a compressed archive in ZIP format.
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

    def get_archiver(self):
        """
        Return archiver Command class object.
        """
        return self._archiver

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Make a compressed archive in ZIP format.')

        parser.add_argument(
            'archive',
            nargs=1,
            metavar='file.zip',
            help='Archive file or directory.'
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
        if os.name == 'nt':
            self._archiver = command_mod.Command(
                'pkzip32.exe',
                errors='ignore'
            )
            if self._archiver.is_found():
                self._archiver.set_args(
                    ['-add', '-maximum', '-recurse', '-path'])
            else:
                self._archiver = command_mod.Command(
                    'zip',
                    args=['-r', '-9'],
                    errors='stop'
                )
        else:
            self._archiver = command_mod.Command(
                'zip',
                args=['-r', '-9'],
                errors='stop'
            )

        if len(args) > 1 and args[1] in ('-add', '-r'):
            subtask_mod.Exec(self._archiver.get_cmdline() + args[1:]).run()

        self._parse_args(args[1:])

        if os.path.isdir(self._args.archive[0]):
            self._archive = os.path.abspath(self._args.archive[0]) + '.zip'
        else:
            self._archive = self._args.archive[0]
        if not self._archive.endswith('.zip'):
            raise SystemExit(
                sys.argv[0] + ': Unsupported "' + self._archive +
                '" archive format.'
            )

        self._archiver.append_arg(self._archive)
        if self._args.files:
            self._archiver.extend_args(self._args.files)
        else:
            self._archiver.extend_args(os.listdir())


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

        task = subtask_mod.Exec(options.get_archiver().get_cmdline())
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
