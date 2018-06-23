#!/usr/bin/env python3
"""
Copy file from clipboard location.
"""

import argparse
import os
import shutil
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

    def get_directory(self):
        """
        Return directory.
        """
        return self._args.directory[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Copy file from clipboard location to directory.')

        parser.add_argument(
            'directory',
            nargs=1,
            help='Directory to copy file.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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

    @staticmethod
    def run():
        """
        Start program
        """
        options = Options()

        xclip = command_mod.Command('xclip', errors='stop')
        xclip.set_args(['-out', '-selection', '-c', 'test'])
        task = subtask_mod.Batch(xclip.get_cmdline())
        task.run()

        source = ''.join(task.get_output())
        if os.path.isfile(source):
            target = os.path.join(
                options.get_directory(),
                os.path.basename(source),
            )

            print('Copying "{0:s}" file to "{1:s}"...'.format(source, target))
            try:
                shutil.copy2(source, target)
            except shutil.Error:
                raise SystemExit(
                    sys.argv[0] + ': Cannot copy to "' + target + '" file.')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
