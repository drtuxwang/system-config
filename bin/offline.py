#!/usr/bin/env python3
"""
Run a command without network access.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_command(self):
        """
        Return command Command class object.
        """
        return self._command

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Run a command without network access.')

        parser.add_argument(
            'command',
            nargs=1,
            help='Command to run.'
        )
        parser.add_argument(
            'args',
            nargs='*',
            metavar='arg',
            help='Command argument.'
        )

        my_args = []
        for arg in args:
            my_args.append(arg)
            if not arg.startswith('-'):
                break

        self._args = parser.parse_args(my_args)

        return args[len(my_args):]

    @staticmethod
    def _get_command(directory, command):
        if os.path.isfile(command):
            return command_mod.CommandFile(os.path.abspath(command))

        file = os.path.join(directory, command)
        if os.path.isfile(file):
            return command_mod.CommandFile(file)
        return command_mod.Command(command)

    def parse(self, args):
        """
        Parse arguments
        """
        command_args = self._parse_args(args[1:])

        self._command = self._get_command(
            os.path.dirname(args[0]),
            self._args.command[0]
        )
        self._command.set_args(command_args)


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
    def _get_unshare():
        unshare = command_mod.Command('unshare', errors='ignore')
        if unshare.is_found():
            task = subtask_mod.Batch(unshare.get_cmdline() + ['--help'])
            task.run(pattern='--map-root-user')
            if task.has_output():
                return unshare.get_cmdline() + ['--net', '--map-root-user']
        return []

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()

        cmdline = cls._get_unshare()
        if cmdline:
            print('Unsharing network namespace...')
        task = subtask_mod.Exec(cmdline + options.get_command().get_cmdline())
        task.run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
