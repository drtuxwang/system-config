#!/usr/bin/env python3
"""
Make a compressed archive in ZIP format.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


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

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Make a compressed archive in ZIP format.')

        parser.add_argument('archive', nargs=1, metavar='file.zip',
                            help='Archive file or directory.')
        parser.add_argument('files', nargs='*', metavar='file', help='File or directory.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        if os.name == 'nt':
            self._archiver = command_mod.Command('pkzip32.exe', errors='ignore')
            if self._archiver.is_found():
                self._archiver.set_args(['-add', '-maximum', '-recurse', '-path'])
            else:
                self._archiver = command_mod.Command('zip', args=['-r', '-9'], errors='stop')
        else:
            self._archiver = command_mod.Command('zip', args=['-r', '-9'], errors='stop')

        if len(args) > 1 and args[1] in ('-add', '-r'):
            subtask_mod.Exec(self._archiver.get_cmdline() + args[1:]).run()

        self._parse_args(args[1:])

        if os.path.isdir(self._args.archive[0]):
            self._archiver.append_arg(os.path.abspath(self._args.archive[0] + '.7z'))
        else:
            self._archiver.append_arg(self._args.archive[0])

        if self._args.files:
            self._archiver.extend_args(self._args.files)
        else:
            self._archiver.extend_args(os.listdir())


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
    def run():
        """
        Start program
        """
        options = Options()

        print('debugX', options.get_archiver().get_cmdline())
        subtask_mod.Exec(options.get_archiver().get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
