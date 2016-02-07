#!/usr/bin/env python3
"""
Securely mount a file system using SSH protocol.
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

    def get_sshfs(self):
        """
        Return sshfs Command class object.
        """
        return self._sshfs

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Securely mount a file system using SSH protocol.')

        parser.add_argument('remote', nargs=1, metavar='user@host:/remotepath',
                            help='Remote directory.')
        parser.add_argument('local', nargs=1, metavar='user@host:/localpath',
                            help='Local directory.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        if len(args) == 1:
            mount = syslib.Command('mount')
            mount.run(filter='type fuse.sshfs ', mode='batch')
            if mount.get_exitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(mount.get_exitcode()) +
                                 ' received from "' + mount.get_file() + '".')
            for line in mount.get_output():
                print(line)
            raise SystemExit(0)

        self._parse_args(args[1:])

        command = syslib.Command('id')
        command.set_args(['-u'])
        command.run(mode='batch')
        if command.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(command.get_exitcode()) +
                             ' received from "' + command.get_file() + '".')
        uid = command.get_output()[0]
        command.set_args(['-g'])
        command.run(mode='batch')
        if command.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(command.get_exitcode()) +
                             ' received from "' + command.get_file() + '".')
        gid = command.get_output()[0]

        self._sshfs = syslib.Command('sshfs')
        self._sshfs.set_args(['-o', 'uid=' + uid + ',gid=' + gid + ',nonempty,reconnect'] +
                             self._args.remote + self._args.local)


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

        options.get_sshfs().run(mode='exec')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
