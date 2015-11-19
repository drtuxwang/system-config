#!/usr/bin/env python3
"""
Run a command immune to terminal hangups.
"""

import argparse
import glob
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

        command = self._args.command[0]
        if os.path.isfile(command):
            self._command = syslib.Command(file=os.path.abspath(command), args=self._commandArgs)
        else:
            file = os.path.join(os.path.dirname(args[0]), command)
            if os.path.isfile(file):
                self._command = syslib.Command(file=file, args=self._commandArgs)
            else:
                self._command = syslib.Command(command, args=self._commandArgs)

        self._sh(self._command)

        if self._args.logFile:
            try:
                with open(self._args.logFile, 'wb'):
                    pass
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + self._logFile + '" logfile file.')

    def getLogFile(self):
        """
        Return log file.
        """
        return self._args.logFile

    def getCommand(self):
        """
        Return command Command class object.
        """
        return self._command

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Run a command immune to terminal hangups.')

        parser.add_argument('-q', action='store_const', const='', dest='logFile',
                            default='run.out', help="Do not create 'run.out' output file.")

        parser.add_argument('command', nargs=1, help='Command to run.')
        parser.add_argument('args', nargs='*', metavar='arg', help='Command argument.')

        myArgs = []
        for arg in args:
            myArgs.append(arg)
            if not arg.startswith('-'):
                break
        self._args = parser.parse_args(myArgs)

        self._commandArgs = args[len(myArgs):]

    def _sh(self, command):
        try:
            with open(command.getFile(), errors='replace') as ifile:
                line = ifile.readline().rstrip('\r\n')
                if line == '#!/bin/sh':
                    sh = syslib.Command(file='/bin/sh')
                    command.setWrapper(sh)
        except IOError:
            pass


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            options.getCommand().run(logfile=options.getLogFile(), mode='daemon')
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
