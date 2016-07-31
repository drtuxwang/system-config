#!/usr/bin/env python3
"""
Securely backup/restore partitions using SSH protocol.
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

    def get_command_1(self):
        """
        Return command1 Command class object.
        """
        return self._command1

    def get_command_2(self):
        """
        Return command2 Command class object.
        """
        return self._command2

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Securely backup/restore partitions using '
            'SSH protocol.'
        )

        parser.add_argument(
            'source',
            nargs=1,
            metavar='[[user1@]host1:]source',
            help='Source device/file location.'
        )
        parser.add_argument(
            'target',
            nargs=1,
            metavar='[[user1@]host1:]target',
            help='Target device/file location.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        source = self._args.source[0]
        target = self._args.target[0]
        if ':' in source:
            if ':' in target:
                raise SystemExit(
                    sys.argv[0] +
                    ': Source or target cannot both be remote device/file.'
                )
            host, file = source.split(':')[:2]
            device = target
            print('Restoring "' + device + '" from', host + ':' + file + '...')
            self._command1 = command_mod.Command(
                'ssh',
                args=[host, 'cat ' + file],
                errors='stop'
            )
            self._command2 = command_mod.Command(
                'dd',
                args=['of=' + device],
                errors='stop'
            )
        else:
            if ':' not in target:
                raise SystemExit(
                    sys.argv[0] +
                    ': Source or target cannot both be local device/file.'
                )
            elif not os.path.exists(source):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + source +
                    '" device or file.'
                )
            device = source
            host, file = target.split(':')[:2]
            print('Backing up "' + device + '" to', host + ':' + file + '...')
            self._command1 = command_mod.Command(
                'dd',
                args=['if=' + device],
                errors='stop'
            )
            self._command2 = command_mod.Command(
                'ssh',
                args=[host, 'cat - > ' + file],
                errors='stop'
            )


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

        task = subtask_mod.Task(options.get_command_1().get_cmdline() + ['|'] +
                                options.get_command_2().get_cmdline())
        task.run()
        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
