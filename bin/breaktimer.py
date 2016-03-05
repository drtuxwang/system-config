#!/usr/bin/env python3
"""
Break reminder timer.
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

FG_COLOUR = '#000000'
BG_COLOUR = '#ffffdd'


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_pop(self):
        """
        Return pop Command class object.
        """
        return self._pop

    def get_time(self):
        """
        Return time limit.
        """
        return self._args.time[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Break reminder timer.')

        parser.add_argument('-g', dest='guiFlag', action='store_true', help='Start GUI.')

        parser.add_argument('time', nargs=1, type=int, help='Time between breaks in minutes.')

        self._args = parser.parse_args(args)

        if self._args.time[0] < 1:
            raise SystemExit(sys.argv[0] + ': You must specific a positive integer for '
                             'break time.')

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        if self._args.guiFlag:
            xterm = syslib.Command('xterm')
            xterm.set_args([
                '-fn', '-misc-fixed-bold-r-normal--18-*-iso8859-1', '-fg', FG_COLOUR,
                '-bg', BG_COLOUR, '-cr', '#880000', '-geometry', '15x3', '-ut', '+sb',
                '-e', sys.argv[0]] + args[2:])
            xterm.run(mode='daemon')
            raise SystemExit(0)

        self._pop = syslib.Command('notify-send')
        self._pop.set_flags(['-t', '10000'])  # 10 seconds display time


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

    def _alert(self):
        if self._alarm < 601:
            sys.stdout.write('\033]11;#ff8888\007')
            sys.stdout.flush()
            self._bell.run(mode='batch')  # Avoids defunct process
            self._options.get_pop().set_args([time.strftime('%H:%M') + ': break time reminder'])
            # Avoids defunct process
            self._options.get_pop().run(mode='batch')
        self._alarm += 60  # One minute reminder

    def run(self):
        """
        Start program
        """
        self._options = Options()
        self._bell = syslib.Command('bell')
        self._limit = self._options.get_time() * 60
        self._alarm = None

        while True:
            sys.stdout.write('\033]11;#ffffdd\007')
            start = int(time.time())
            elapsed = 0
            self._alarm = 0

            try:
                while True:
                    if elapsed >= self._limit + self._alarm:
                        self._alert()
                    time.sleep(1)
                    elapsed = int(time.time()) - start
                    sys.stdout.write(
                        ' \r ' + time.strftime('%H:%M ') + str(self._limit - elapsed))
                    sys.stdout.flush()
            except KeyboardInterrupt:
                print()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
