#!/usr/bin/env python3
"""
Send popup message to display.
"""

import argparse
import glob
import os
import signal
import sys
import time


import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_pop(self):
        """
        Return pop Command class object.
        """
        return self._pop

    def get_time_delay(self):
        """
        Return time delay in minutes.
        """
        return self._args.timeDelay[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Send popup message to display.')

        parser.add_argument(
            '-time',
            nargs=1,
            type=int,
            dest='timeDelay',
            default=[0],
            help='Delay popup in minutes.'
        )
        parser.add_argument(
            'words',
            nargs='+',
            metavar='word',
            help='A word.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._pop = command_mod.Command('notify-send', errors='stop')
        self._pop.set_args(['--expire-time=0'] + self._args.words)

        if self._args.timeDelay[0] < 0:
            raise SystemExit(
                sys.argv[0] +
                ': You must specific a positive integer for delay time.'
            )


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
        bell = command_mod.Command('bell', errors='ignore')
        pop = options.get_pop()
        delay = 60 * options.get_time_delay()

        time.sleep(delay)

        if bell.is_found():
            subtask_mod.Background(bell.get_cmdline()).run()

        task = subtask_mod.Task(pop.get_cmdline())
        task.run()
        if task.get_exitcode():
            raise SystemExit(
                sys.argv[0] + ': Error code ' + str(task.get_exitcode()) +
                ' received from "' + task.get_file() + '".'
            )


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
