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

import coloredlogs

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")

# pylint: disable=invalid-name
logger = logging.getLogger(__name__)
# pylint: enable=invalid-name
coloredlogs.install(
    logger=logger,
    level='INFO',
    milliseconds=True,
    fmt='%(asctime)s %(levelname)-8s %(message)s',
    field_styles={
        'asctime': {'color': 'green'},
        'levelname': {'color': 'black', 'bold': True},
    },
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
