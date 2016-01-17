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

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._ntpdate = syslib.Command('ntpdate', pathextra=['/usr/sbin'])
        self._ntpdate.set_args(['pool.ntp.org'])

        if len(args) == 1 or args[1] != '-u':
            self._ntpdate.run(mode='exec')

    def get_ntpdate(self):
        """
        Return ntpdate Command class object.
        """
        return self._ntpdate


class Update(object):
    """
    Update class
    """

    def __init__(self, options):
        while True:
            options.get_ntpdate().run(mode='batch')
            if not options.get_ntpdate().has_error():
                print('NTP Time updated =', time.strftime('%Y-%m-%d-%H:%M:%S'))
                time.sleep(86340)
            time.sleep(60)


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            Update(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
