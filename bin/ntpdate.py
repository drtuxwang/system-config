#!/usr/bin/env python3
"""
Run daemon to update time once every 24 hours
"""

import glob
import os
import signal
import sys
import time

import syslib

if sys.version_info < (3, 0) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.0, < 4.0).')


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
        except (syslib.SyslibError, SystemExit) as exception:
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
        ntpdate = syslib.Command('ntpdate', pathextra=['/usr/sbin'])
        ntpdate.set_args(['pool.ntp.org'])

        if len(sys.argv) == 1 or sys.argv[1] != '-u':
            ntpdate.run(mode='exec')

        while True:
            ntpdate.run(mode='batch')
            if not ntpdate.has_error():
                print('NTP Time updated =', time.strftime('%Y-%m-%d-%H:%M:%S'))
                time.sleep(86340)
            time.sleep(60)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
