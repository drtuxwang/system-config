#!/usr/bin/env python3
"""
Wait for task to finish then launch command.
"""

import argparse
import glob
import os
import signal
import sys
import time

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        self._pid = 0
        self._pname = ''
        try:
            self._pid = int(self._args.task[0])
        except ValueError:
            self._pname = self._args.task[0]

        self._command = syslib.Command(self._args.command[0], args=self._command_args)

    def get_command(self):
        """
        Return command Command class object.
        """
        return self._command

    def get_pid(self):
        """
        Return process ID.
        """
        return self._pid

    def get_pname(self):
        """
        Return process command name.
        """
        return self._pname

    def get_user(self):
        """
        Return user name.
        """
        return self._args.user

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Wait for task to finish then launch command.')

        parser.add_argument('-a', dest='user', action='store_const', const='<all>', default='',
                            help='Monitor any user"s process.')

        parser.add_argument('task', nargs=1, metavar='pid|pname', help='Process ID or name.')
        parser.add_argument('command', nargs=1, help='Command name.')
        parser.add_argument('commandArgs', nargs='*', metavar='arg', help='Command arguments.')

        self._args = parser.parse_args(args[:2])
        self._command_args = args[2:]


class Waitfor(object):
    """
    Wait class
    """

    def __init__(self, options):
        user = options.get_user()
        pname = options.get_pname()

        if pname:
            while syslib.Task(user).haspname(pname):
                time.sleep(1)
        else:
            pid = options.get_pid()
            while pid in syslib.Task(user).get_pids():
                time.sleep(1)
        options.get_command().run(mode='exec')


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
            Waitfor(options)
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
