#!/usr/bin/env python3
"""
Run daemon to update time once every 24 hours
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

# pylint: disable = invalid-name
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
# pylint: enable = invalid-name
console_handler.setFormatter(logging_mod.ColoredFormatter())
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


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
        ntpdate = command_mod.Command(
            'ntpdate',
            pathextra=['/usr/sbin'],
            args=['pool.ntp.org'],
            errors='stop'
        )
        if len(sys.argv) == 1 or sys.argv[1] != '-u':
            subtask_mod.Exec(ntpdate.get_cmdline() + sys.argv[1:]).run()

        task = subtask_mod.Task(ntpdate.get_cmdline())
        hwclock = command_mod.Command('hwclock', errors='stop')
        while True:
            task.run()
            if not task.has_error():
                subtask_mod.Task(hwclock.get_cmdline() + ['-w']).run()
                subtask_mod.Task(hwclock.get_cmdline()).run()
                logger.info(
                    'System & HWClock time updated: %s',
                    time.strftime('%Y-%m-%d-%H:%M:%S'),
                )
                time.sleep(86340)
            time.sleep(60)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
