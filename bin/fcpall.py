#!/usr/bin/env python3
"""
Copy a file to multiple target files.
"""

import argparse
import glob
import os
import shutil
import signal
import sys


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_source(self):
        """
        Return source file.
        """
        return self._args.source[0]

    def get_targets(self):
        """
        Return target files.
        """
        return self._args.targets

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Copy a file to multiple target files.')

        parser.add_argument(
            'source',
            nargs=1,
            help='Source file.'
        )
        parser.add_argument(
            'targets',
            nargs='+',
            metavar='target',
            help='Target file.'
        )

        self._args = parser.parse_args(args)

        if not os.path.isfile(self._args.source[0]):
            raise SystemExit(
                sys.argv[0] + ': Cannot find "' + self._args.source[0] +
                '" file.'
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

    @staticmethod
    def _copy(source, target):
        print('Copying to "' + target + '" file...')
        try:
            shutil.copy2(source, target)
        except shutil.Error as exception:
            if 'are the same file' in exception.args[0]:
                raise SystemExit(
                    sys.argv[0] + ': Cannot copy to same "' +
                    target + '" file.'
                ) from exception
            raise SystemExit(
                sys.argv[0] + ': Cannot copy to "' +
                target + '" file.'
            ) from exception
        except OSError as exception:
            if exception.args != (95, 'Operation not supported'):
                try:
                    with open(source, 'rb'):
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create "' +
                            target + '" file.'
                        ) from exception
                except OSError as exception:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot create "' + target + '" file.'
                    ) from exception

    def run(self):
        """
        Start program
        """
        options = Options()
        source = options.get_source()
        for target in options.get_targets():
            self._copy(source, target)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
