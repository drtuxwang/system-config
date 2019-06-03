#!/usr/bin/env python3
"""
Unmount file system securely mounted with SSH protocol.
"""

import argparse
import glob
import os
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

    def get_directories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Unmount file system securely mounted with '
            'SSH protocol.'
        )

        parser.add_argument(
            'directories',
            nargs='+',
            metavar='localpath',
            help='Local directory.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._directories = []
        for directory in args[1:]:
            self._directories.append(os.path.abspath(directory))


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

        directories = options.get_directories()
        mount = command_mod.Command('mount', errors='stop')
        fusermount = command_mod.Command('fusermount', errors='stop')

        for directory in directories:
            task = subtask_mod.Batch(mount.get_cmdline())
            task.run(pattern=' ' + directory + ' type fuse.sshfs ')
            if not task.has_output():
                raise SystemExit(
                    sys.argv[0] + ': "' + directory +
                    '" is not a mount point.'
                )
            if task.get_exitcode():
                raise SystemExit(
                    sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                    ' received from "' + task.get_file() + '".'
                )
            fusermount.set_args(['-u', directory])
            subtask_mod.Task(fusermount.get_cmdline()).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
