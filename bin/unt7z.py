#!/usr/bin/env python3
"""
Unpack a compressed archive in TAR.7Z format.
"""

import argparse
import glob
import os
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
        parser = argparse.ArgumentParser(
            description='Unpack a compressed archive in TAR.7Z format.'
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='Show contents of archive.'
        )
        parser.add_argument(
            'archives',
            nargs='+',
            metavar='file.tar.7z|file.t7z',
            help='Archive file.'
        )

        self._args = parser.parse_args(args)

        for archive in self._args.archives:
            if not archive.endswith(('.tar.7z', '.t7z')):
                raise SystemExit(
                    sys.argv[0] + ': Unsupported "' + archive +
                    '" archive format.'
                )

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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

    def _unpack(self, archive):
        p7zip = command_mod.Command('7z', errors='stop')
        p7zip.set_args(['x', '-y', '-so', archive])
        self._tar.set_args(['xfv', '-'])
        subtask_mod.Task(
            p7zip.get_cmdline() + ['|'] + self._tar.get_cmdline()
        ).run()

    def _view(self, archive):
        p7zip = command_mod.Command('7z', errors='stop')
        p7zip.set_args(['x', '-y', '-so', archive])
        self._tar.set_args(['tfv', '-'])
        subtask_mod.Task(
            p7zip.get_cmdline() + ['|'] + self._tar.get_cmdline()
        ).run()

    def run(self):
        """
        Start program
        """
        options = Options()

        os.umask(int('022', 8))
        if os.name == 'nt':
            self._tar = command_mod.Command('tar.exe', errors='stop')
        else:
            self._tar = command_mod.Command('tar', errors='stop')

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
