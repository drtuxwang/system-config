#!/usr/bin/env python3
"""
Kill tasks by process ID or name.
"""

import argparse
import glob
import os
import signal
import sys
import time

import task_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_force_flag(self):
        """
        Return force flag.
        """
        return self._args.force_flag

    def get_time_delay(self):
        """
        Return time delay in seconds.
        """
        return self._args.timeDelay[0]

    def get_keywords(self):
        """
        Return process ID or keyword.
        """
        return self._args.task

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Kill tasks by process ID or name.')

        parser.add_argument(
            '-delay',
            nargs=1,
            type=int,
            dest='timeDelay',
            default=[0],
            help='Delay kill in seconds.'
        )
        parser.add_argument(
            '-f',
            dest='force_flag',
            action='store_true',
            help='Force termination of tasks.'
        )
        parser.add_argument(
            'task',
            nargs='+',
            metavar='pid|keyword',
            help='Process ID or keyword.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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
    def _filter(options):
        pids = []
        task = task_mod.Tasks.factory()
        for keyword in options.get_keywords():
            if keyword.isdigit():
                if task.haspid(int(keyword)):
                    pids.append(int(keyword))
            else:
                pids.extend(task.pname2pids('.*' + keyword + '.*'))

        print(
            'RUSER      PID  PPID  PGID PRI  NI TTY      MEMORY  '
            'CPUTIME     ELAPSED COMMAND'
        )
        for pid in pids:
            process = task.get_process(pid)
            print(
                '{0:8s} {1:5d} {2:5d} {3:5d} {4:>3s} {5:>3s} {6:7s} {7:7d} '
                '{8:>8s} {9:>11s} {10:s}'.format(
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
        print()
        return pids

    @staticmethod
    def _ykill(options, pids):
        task = task_mod.Tasks.factory()
        mypid = os.getpid()
        apids = task.get_ancestor_pids(mypid)
        for pid in pids:
            if pid == mypid:
                print("Process", pid, "is my own process ID")
            elif pid in apids:
                print("Process", pid, "is my ancestor process")
            else:
                if not options.get_force_flag():
                    answer = input("Kill process " + str(pid) + " (y/n): ")
                    if answer not in ('y', 'Y'):
                        continue
                task.killpids([pid])
                print("Process", pid, "killed")

    def run(self):
        """
        Start program
        """
        options = Options()

        time.sleep(options.get_time_delay())
        pids = self._filter(options)
        self._ykill(options, pids)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
