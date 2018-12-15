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

import command_mod
import subtask_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options:
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
        parser = argparse.ArgumentParser(
            description='Ping a host until a connection is made.')

        parser.add_argument('host', nargs=1, help='Host name or IP address.')

        self._args = parser.parse_args(args)

    @staticmethod
    def _get_ping():
        if os.path.isfile('/usr/sbin/ping'):
            return command_mod.CommandFile('/usr/sbin/ping')
        if os.path.isfile('/usr/etc/ping'):
            return command_mod.CommandFile('/usr/etc/ping')
        return command_mod.Command('ping')

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        host = self._args.host[0]
        self._ping = self._get_ping()
        self._ping.set_args(['-w', '4', '-c', '3', host])
        self._pattern = 'min/avg/max'

        if os.name == 'nt':
            self._ping.set_args(['-w', '4', '-n', '3', host])
            self._pattern = 'Minimum|TTL'
        else:
            osname = os.uname()[0]
            if osname == 'Darwin':
                self._ping.set_args(['-t', '4', '-c', '3', host])
            elif osname == 'Linux':
                self._ping.set_args(['-w', '4', '-c', '3', host])
            elif osname == 'SunOS':
                self._ping.set_args(['-s', host, '64', '3'])


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

        task = subtask_mod.Batch(options.get_ping().get_cmdline())
        while True:
            task.run(pattern=options.get_pattern())
            if task.has_output():
                break
            time.sleep(5)
        print(task.get_output()[-1].strip())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
