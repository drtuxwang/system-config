#!/usr/bin/env python3
"""
Displays month or year calendar.
"""

import argparse
import glob
import os
import signal
import sys
import time

import calendar

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

        if self._args.year:
            self._year = self._args.year
            if self._year < 2 or self._year > 9999:
                raise SystemExit(sys.argv[0] + ': Invalid "' + str(self._year) +
                                 '" year. Use 2-9999.')
        else:
            self._year = int(time.strftime('%Y'))

        if self._args.month:
            self._month = self._args.month
            if self._month < 1 or self._month > 12:
                raise SystemExit(sys.argv[0] + ': Invalid "' + str(self._month) +
                                 '" month. Use 1-12.')
        elif self._args.year:
            self._month = 0
        else:
            self._month = int(time.strftime('%m'))

    def get_month(self):
        """
        Return month of files.
        """
        return self._month

    def get_year(self):
        """
        Return year of files.
        """
        return self._year

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Displays month or year calendar.')

        parser.add_argument('year', nargs='?', type=int, help='Select year.')
        parser.add_argument('month', nargs='?', type=int, help='Select month.')

        self._args = parser.parse_args(args)


class Calendar(object):
    """
    Calendar class
    """

    def __init__(self, options):
        if options.get_month() == 0:
            print(calendar.TextCalendar(6).formatyear(options.get_year()))
        else:
            print(calendar.TextCalendar(6).formatmonth(options.get_year(), options.get_month()))


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
            Calendar(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
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
