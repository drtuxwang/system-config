#!/usr/bin/env python3
"""
Securely mount a file system using SSH protocol.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import glob
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        if len(args) == 1:
            mount = syslib.Command('mount')
            mount.run(filter='type fuse.sshfs ', mode='batch')
            if mount.getExitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(mount.getExitcode()) +
                                 ' received from "' + mount.getFile() + '".')
            for line in mount.getOutput():
                print(line)
            raise SystemExit(0)

        self._parseArgs(args[1:])

        id = syslib.Command('id')
        id.setArgs(['-u'])
        id.run(mode='batch')
        if id.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(id.getExitcode()) +
                             ' received from "' + id.getFile() + '".')
        uid = id.getOutput()[0]
        id.setArgs(['-g'])
        id.run(mode='batch')
        if id.getExitcode():
            raise SystemExit(sys.argv[0] + ': Error code ' + str(id.getExitcode()) +
                             ' received from "' + id.getFile() + '".')
        gid = id.getOutput()[0]

        self._sshfs = syslib.Command('sshfs')
        self._sshfs.setArgs(['-o', 'uid=' + uid + ',gid=' + gid + ',nonempty,reconnect'] +
                            self._args.remote + self._args.local)

    def getSshfs(self):
        """
        Return sshfs Command class object.
        """
        return self._sshfs

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(
            description='Securely mount a file system using SSH protocol.')

        parser.add_argument('remote', nargs=1, metavar='user@host:/remotepath',
                            help='Remote directory.')
        parser.add_argument('local', nargs=1, metavar='user@host:/localpath',
                            help='Local directory.')

        self._args = parser.parse_args(args)


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getSshfs().run(mode='exec')
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windowsArgv(self):
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
