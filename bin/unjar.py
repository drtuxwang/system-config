#!/usr/bin/env python3
"""
Unpack a compressed JAVA archive in JAR format.
"""

import argparse
import glob
import os
import signal
import sys

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_archiver(self):
        """
        Return archiver Command class object.
        """
        return self._archiver

    def get_archives(self):
        """
        Return list of archive files.
        """
        return self._args.archives

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Unpack a compressed JAVA archive in JAR format.')

        parser.add_argument('-v', dest='view_flag', action='store_true',
                            help='Show contents of archive.')

        parser.add_argument('archives', nargs='+', metavar='file.jar',
                            help='Archive file.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._archiver = command_mod.Command('jar', errors='stop')
        if self._args.view_flag:
            self._archiver.set_args(['tfv'])
        else:
            self._archiver.set_args(['xfv'])


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

        os.umask(int('022', 8))
        cmdline = options.get_archiver().get_cmdline()

        for archive in options.get_archives():
            task = subtask_mod.Task(cmdline + [archive])
            task.run()
            if task.get_exitcode():
                raise SystemExit(sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                                 ' received from "' + task.get_file() + '".')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
