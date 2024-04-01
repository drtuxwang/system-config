#!/usr/bin/env python3
"""
Wrapper for "ntpdate" command
"""

import logging
import signal
import sys
import time

from command_mod import Command
from logging_mod import ColoredFormatter
from subtask_mod import Exec, Task

RELEASE = 20230122

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter())
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

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        ntpdate = Command('ntpdate', pathextra=['/usr/sbin'], errors='stop')
        if len(sys.argv) != 3 or sys.argv[1] != '-b':
            Exec(ntpdate.get_cmdline() + sys.argv[1:]).run()

        task = Task(ntpdate.get_cmdline() + sys.argv[1:])
        hwclock = Command('hwclock', errors='stop')
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
                Task(hwclock.get_cmdline() + ['--systohc']).run()
                Task(hwclock.get_cmdline()).run()
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
