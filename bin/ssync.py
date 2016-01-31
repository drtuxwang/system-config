#!/usr/bin/env python3
"""
Securely synchronize file system using SSH protocol.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_rsync(self):
        """
        Return rsync Command class object.
        """
        return self._rsync

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Securely synchronize file system using SSH protocol.')

        parser.add_argument('source', nargs=1, metavar='[[user1@]host1:]source',
                            help='Source location.')
        parser.add_argument('target', nargs=1, metavar='[[user1@]host1:]target',
                            help='Target location.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        ssh = syslib.Command('ssh')

        self._rsync = syslib.Command('rsync')
        self._rsync.set_flags(
            ['-l', '-p', '-r', '-t', '-v', '-z', '-e', ssh.get_file(), '--delete'])
        self._rsync.set_args([self._args.source[0], self._args.target[0]])


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
        except (syslib.SyslibError, SystemExit) as exception:
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

        options.get_rsync().run(filter='^$')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
