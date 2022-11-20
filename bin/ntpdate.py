#!/usr/bin/env python3
"""
Wrapper for "ntpdate" command
"""

import glob
import logging
import os
import signal
import sys
import time

import command_mod
import logging_mod
import subtask_mod

RELEASE = 20221119

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


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
    def run() -> int:
        """
        Start program
        """
        ntpdate = command_mod.Command(
            'ntpdate',
            pathextra=['/usr/sbin'],
            errors='stop'
        )
        if len(sys.argv) != 3 or sys.argv[1] != '-b':
            subtask_mod.Exec(ntpdate.get_cmdline() + sys.argv[1:]).run()

        task = subtask_mod.Task(ntpdate.get_cmdline() + sys.argv[1:])
        hwclock = command_mod.Command('hwclock', errors='stop')
        if int(time.strftime('%Y%m%d')) < RELEASE:
            logger.info(time.strftime(
                "Current clock is to old (Please check CMOS battery)",
            ))
            retry = 10
        else:
            retry = 60

        while True:
            logger.info("Updating date and time via NTP...")
            task.run()
            date = int(time.strftime('%Y%m%d'))
            if task.get_exitcode() == 0 and date >= RELEASE:
                subtask_mod.Task(hwclock.get_cmdline() + ['--systohc']).run()
                subtask_mod.Task(hwclock.get_cmdline()).run()
                logger.info('System & HWClock time updated!')
                break

            logger.info("Failed - retrying in %d seconds", retry)
            time.sleep(retry)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
