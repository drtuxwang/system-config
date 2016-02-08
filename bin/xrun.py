#!/usr/bin/env python3
"""
Run GUI software and restore resolution.
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

    def get_command(self):
        """
        Return Command class object.
        """
        return self._command

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Run GUI software and restore resolution.')

        parser.add_argument('command', nargs=1, help='Command to run.')
        parser.add_argument('args', nargs='*', metavar='arg', help='Command argument.')

        self._args = parser.parse_args(args[:1])

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        command = self._args.command[0]
        self._command = syslib.Command(command, pathextra=[command], args=args[2:])


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
        command = options.get_command()

        xrandr = syslib.Command('xrandr')
        xrandr.run(filter='^  ', mode='batch')
        resolution = 0
        for line in xrandr.get_output():
            if '*' in line:
                break
            resolution += 1
        dpi = '96'

        xrdb = syslib.Command('xrdb', args=['-query'], check=False)
        if xrdb.is_found():
            xrdb.run(mode='batch', filter='^Xft.dpi:\t')
            if xrdb.has_output():
                dpi = xrdb.get_output()[0].split()[1]

        command.run()
        xrandr.run(filter='^  ', mode='batch')
        resolution = 0

        for line in xrandr.get_output():
            if '*' in line:
                break
            resolution += 1

        if resolution != resolution:
            time.sleep(1)
            if resolution != 0:
                xrandr.set_args(['-s', '0'])
                xrandr.run(mode='batch')
                time.sleep(1)
            xrandr.set_args(['-s', str(resolution)])
            xrandr.run(mode='batch')

        time.sleep(1)
        xrandr.set_args(['--dpi', dpi])
        xrandr.run(mode='batch')


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
