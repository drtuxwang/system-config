#!/usr/bin/env python3
"""
Show all tasks belonging to an user.
"""

import argparse
import glob
import os
import signal
import sys

import task_mod


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_task(self):
        """
        Return task Task class object.
        """
        return self._task

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Show all tasks belonging to an user.')

        parser.add_argument(
            '-a',
            dest='all_flag',
            action='store_true',
            help='Show task list for all users.'
        )

        parser.add_argument('username', nargs='?', help='user name.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.username:
            self._task = task_mod.Tasks.factory(self._args.username)
        elif self._args.all_flag:
            self._task = task_mod.Tasks.factory('<all>')
        else:
            self._task = task_mod.Tasks.factory()


class Main:
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
        task = options.get_task()

        try:
            print(
                'RUSER      PID  PPID  PGID PRI  NI TTY      MEMORY  '
                'CPUTIME     ELAPSED COMMAND'
            )
            for pid in task.get_pids():
                process = task.get_process(pid)
                print(
                    '{0:8s} {1:5d} {2:5d} {3:5d} {4:>3s} {5:>3s} {6:7s} '
                    '{7:7d} {8:>8s} {9:>11s} {10:s}'.format(
                        process['USER'].split()[0],
                        pid,
                        process['PPID'],
                        process['PGID'],
                        process['PRI'],
                        process['NICE'],
                        process['TTY'],
                        process['MEMORY'],
                        process['CPUTIME'],
                        process['ETIME'],
                        process['COMMAND']
                    )
                )
        except OSError:
            pass


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
