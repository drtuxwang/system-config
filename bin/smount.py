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

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
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

        id = syslib.Command('id')
        id.set_args(['-u'])
        id.run(mode='batch')
        if id.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(id.get_exitcode()) +
                             ' received from "' + id.get_file() + '".')
        uid = id.get_output()[0]
        id.set_args(['-g'])
        id.run(mode='batch')
        if id.get_exitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(id.get_exitcode()) +
                             ' received from "' + id.get_file() + '".')
        gid = id.get_output()[0]

        self._sshfs = syslib.Command('sshfs')
        self._sshfs.set_args(['-o', 'uid=' + uid + ',gid=' + gid + ',nonempty,reconnect'] +
                             self._args.remote + self._args.local)

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
            options.get_sshfs().run(mode='exec')
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
