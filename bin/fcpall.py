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

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

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
        parser = argparse.ArgumentParser(description='Copy a file to multiple target files.')

        parser.add_argument('source', nargs=1, help='Source file.')
        parser.add_argument('targets', nargs='+', metavar='target', help='Target file.')

        self._args = parser.parse_args(args)

        if not os.path.isfile(self._args.source[0]):
            raise SystemExit(sys.argv[0] + ': Cannot find "' + self._args.source + '" file.')


class Copy(object):
    """
    Copy class
    """

    def __init__(self, options):
        self._options = options

        source = options.get_source()
        for target in options.get_targets():
            self._copy(source, target)

    def _copy(self, source, target):
        print('Copying to "' + target + '" file...')
        try:
            shutil.copy2(source, target)
        except shutil.Error as exception:
            if 'are the same file' in exception.args[0]:
                raise SystemExit(sys.argv[0] + ': Cannot copy to same "' + target + '" file.')
            else:
                raise SystemExit(sys.argv[0] + ': Cannot copy to "' + target + '" file.')
        except OSError as exception:
            if exception.args != (95, 'Operation not supported'):  # os.listxattr for ACL
                try:
                    with open(source, 'rb'):
                        raise SystemExit(sys.argv[0] + ': Cannot create "' + target + '" file.')
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + target + '" file.')


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            Copy(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
