#!/usr/bin/env python3
"""
Print large monthly calendar.
"""

import sys
if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')
if __name__ == '__main__':
    sys.path = sys.path[1:] + sys.path[:1]

import argparse
import calendar
import glob
import os
import signal

import syslib


class Options(syslib.Dump):

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getMonth(self):
        """
        Return month of files.
        """
        return self._args.month[0]

    def getYear(self):
        """
        Return year of files.
        """
        return self._args.year[0]

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Print large monthly calendar.')

        parser.add_argument('year', nargs=1, type=int, help='Select year.')
        parser.add_argument('month', nargs=1, type=int, help='Select month.')

        self._args = parser.parse_args(args)

        year = self._args.year[0]
        if year < 2 or year > 9999:
            raise SystemExit(sys.argv[0] + ': Invalid "' + str(year) + '" year. Use 2-9999.')

        month = self._args.month[0]
        if month < 1 or month > 12:
            raise SystemExit(sys.argv[0] + ': Invalid "' + str(month) + '" month. Use 1-12.')


class Calendar(syslib.Dump):

    def __init__(self, options):
        print('\n                  [ ', calendar.month_name[options.getMonth()] + ' ',
              options.getYear(), ' ]\n')
        for line in calendar.TextCalendar(6).formatmonth(
                options.getYear(), options.getMonth()).split(os.linesep)[1:]:
            print('  __________________________________________________  ', line)
        print()
        print('  ____________________________________________________________________________ ')
        print(' |          |          |          |          |          |          |          |')
        print(' |          |          |          |          |          |          |          |')
        print(' | Sunday   | Monday   | Tuesday  | Wednesday| Thursday | Friday   | Saturday |')
        print(' |          |          |          |          |          |          |          |')
        print(' |__________|__________|__________|__________|__________|__________|__________|')
        for week in calendar.Calendar(6).monthdays2calendar(options.getYear(), options.getMonth()):
            print(' |          |          |          |          |          |          |          |')
            line = ''
            for day in week:
                if day[0] == 0:
                    line += ' |         '
                else:
                    line += ' | ' + str(day[0]).ljust(8)
            line += ' |'
            print(line)
            for i in range(5):
                print(' |' + 7*'          |')
            print(' |' + 7*'__________|')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
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

    def _windowsArgv(self):
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
