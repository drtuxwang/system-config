#!/usr/bin/env python3
"""
Kill tasks by process ID or name.
"""

import argparse
import os
import signal
import sys
import time
from typing import List

from task_mod import Tasks


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_force_flag(self) -> bool:
        """
        Return force flag.
        """
        return self._args.force_flag

    def get_time_delay(self) -> int:
        """
        Return time delay in seconds.
        """
        return self._args.timeDelay[0]

    def get_keywords(self) -> List[str]:
        """
        Return process ID or keyword.
        """
        return self._args.task

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Kill tasks by process ID or name.",
        )

        parser.add_argument(
            '-delay',
            nargs=1,
            type=int,
            dest='timeDelay',
            default=[0],
            help="Delay kill in seconds.",
        )
        parser.add_argument(
            '-f',
            dest='force_flag',
            action='store_true',
            help="Force termination of tasks.",
        )
        parser.add_argument(
            'task',
            nargs='+',
            metavar='pid|keyword',
            help="Process ID or keyword.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    @staticmethod
    def _filter(options: Options) -> List[int]:
        pids = []
        task = Tasks.factory()
        for keyword in options.get_keywords():
            if keyword.isdigit():
                if task.haspid(int(keyword)):
                    pids.append(int(keyword))
            else:
                pids.extend(task.pname2pids(f'.*{keyword}.*'))

        print(
            'RUSER      PID  PPID  PGID PRI  NI TTY      MEMORY  '
            'CPUTIME     ELAPSED COMMAND'
        )
        for pid in pids:
            process = task.get_process(pid)
            print(
                f"{process['USER'].split()[0]:8s} "
                f"{pid:5d} "
                f"{process['PPID']:5d} "
                f"{process['PGID']:5d} "
                f"{process['PRI']:>3s} "
                f"{process['NICE']:>3s} "
                f"{process['TTY']:7s} "
                f"{process['MEMORY']:7d} "
                f"{process['CPUTIME']:>8s} "
                f"{process['ETIME']:>11s} "
                f"{process['COMMAND']}",
            )
        print()
        return pids

    @staticmethod
    def _ykill(options: Options, pids: List[int]) -> None:
        task = Tasks.factory()
        mypid = os.getpid()
        apids = task.get_ancestor_pids(mypid)
        for pid in pids:
            if pid == mypid:
                print("Process", pid, "is my own process ID")
            elif pid in apids:
                print("Process", pid, "is my ancestor process")
            else:
                if not options.get_force_flag():
                    answer = input(f"Kill process {pid} (y/n): ")
                    if answer not in ('y', 'Y'):
                        continue
                task.killpids([pid])
                print("Process", pid, "killed")

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        time.sleep(options.get_time_delay())
        pids = self._filter(options)
        self._ykill(options, pids)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
