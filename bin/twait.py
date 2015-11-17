#!/usr/bin/env python3
"""
Wait for task to finish then launch command.
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
import time

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

        self._pid = 0
        self._pname = ''
        try:
            self._pid = int(self._args.task[0])
        except ValueError:
            self._pname = self._args.task[0]

        self._command = syslib.Command(self._args.command[0], args=self._commandArgs)

    def getCommand(self):
        """
        Return command Command class object.
        """
        return self._command

    def getPid(self):
        """
        Return process ID.
        """
        return self._pid

    def getPname(self):
        """
        Return process command name.
        """
        return self._pname

    def getUser(self):
        """
        Return user name.
        """
        return self._args.user

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Wait for task to finish then launch command.')

        parser.add_argument('-a', dest='user', action='store_const', const='<all>', default='',
                            help='Monitor any user"s process.')

        parser.add_argument('task', nargs=1, metavar='pid|pname', help='Process ID or name.')
        parser.add_argument('command', nargs=1, help='Command name.')
        parser.add_argument('commandArgs', nargs='*', metavar='arg', help='Command arguments.')

        self._args = parser.parse_args(args[:2])
        self._commandArgs = args[2:]


class Waitfor(syslib.Dump):

    def __init__(self, options):
        user = options.getUser()
        pname = options.getPname()

        if pname:
            while syslib.Task(user).haspname(pname):
                time.sleep(1)
        else:
            pid = options.getPid()
            while pid in syslib.Task(user).getPids():
                time.sleep(1)
        options.getCommand().run(mode='exec')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Waitfor(options)
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
