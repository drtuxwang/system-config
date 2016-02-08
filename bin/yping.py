#!/usr/bin/env python3
"""
Ping a host until a connection is made.
"""

import argparse
import glob
import os
import signal
import sys
import time

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_pattern(self):
        """
        Return filter pattern.
        """
        return self._pattern

    def get_ping(self):
        """
        Return ping Command class object.
        """
        return self._ping

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Ping a host until a connection is made.')

        parser.add_argument('host', nargs=1, help='Host name or IP address.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if os.path.isfile('/usr/sbin/ping'):
            self._ping = syslib.Command(file='/usr/sbin/ping')
        elif os.path.isfile('/usr/etc/ping'):
            self._ping = syslib.Command(file='/usr/etc/ping')
        else:
            self._ping = syslib.Command('ping')

        self._pattern = 'min/avg/max'

        host = self._args.host[0]
        if syslib.info.get_system() == 'macos':
            self._ping.set_args(['-t', '4', '-c', '3', host])
        elif syslib.info.get_system() == 'linux':
            self._ping.set_args(['-w', '4', '-c', '3', host])
        elif syslib.info.get_system() == 'sunos':
            self._ping.set_args(['-s', host, '64', '3'])
        elif os.name == 'nt':
            self._ping.set_args(['-w', '4', '-n', '3', host])
            self._pattern = 'Minimum|TTL'
        else:
            self._ping.set_args(['-w', '4', '-c', '3', host])


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

        ping = options.get_ping()
        while True:
            ping.run(filter=options.get_pattern(), mode='batch')
            if ping.has_output():
                break
            time.sleep(5)
        print(ping.get_output()[-1].strip())
