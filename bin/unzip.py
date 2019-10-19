#!/usr/bin/env python3
"""
Unpack a compressed archive in ZIP format.
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

    def get_archiver(self):
        """
        Return archiver Command class object.
        """
        return self._archiver

    def get_archives(self):
        """
        Return list of archive files.
        """
        return self._args.archives

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Unpack a compressed archive in ZIP format.')

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='Show contents of archive.'
        )
        parser.add_argument(
            '-test',
            dest='test_flag',
            action='store_true',
            help='Test archive data only.'
        )
        parser.add_argument(
            'archives',
            nargs='+',
            metavar='file.zip',
            help='Archive file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if os.name == 'nt':
            self._archiver = command_mod.Command(
                'pkzip32.exe',
                errors='ignore'
            )
            if not self._archiver.is_found():
                self._archiver = command_mod.Command('unzip', errors='stop')
        else:
            self._archiver = command_mod.Command('unzip', errors='stop')

        if args[1] in ('view', 'test'):
            self._archiver.set_args(args[1:])
            subtask_mod.Exec(self._archiver.get_cmdline()).run()

        if os.path.basename(self._archiver.get_file()) == 'pkzip32.exe':
            if self._args.view_flag:
                self._archiver.set_args(['-view'])
            elif self._args.test_flag:
                self._archiver.set_args(['-test'])
            else:
                self._archiver.set_args(['-extract', '-directories'])
        else:
            if self._args.view_flag:
                self._archiver.set_args(['-v'])
            elif self._args.test_flag:
                self._archiver.set_args(['-t'])


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
        cmdline = options.get_archiver().get_cmdline()
        for archive in options.get_archives():
            task = subtask_mod.Task(cmdline + [archive])
            task.run()
            if task.get_exitcode():
                print(
                    sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                    ' received from "' + task.get_file() + '".',
                    file=sys.stderr
                )
                raise SystemExit(task.get_exitcode())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
