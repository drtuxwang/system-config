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


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_long_flag(self):
        """
        Return long flag.
        """
        return self._args.long_flag

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

        parser.add_argument('-l', dest='long_flag', action='store_true',
                            help='Select long output.')

        parser.add_argument('year', nargs='?', type=int, help='Select year.')
        parser.add_argument('month', nargs='?', type=int, help='Select month.')

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
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
    def _long(year, month):
        if not month:
            month = int(time.strftime('%m'))
        print('\n                  [ ', calendar.month_name[month] + ' ', year, ' ]\n')
        for line in calendar.TextCalendar(6).formatmonth(year, month).split(os.linesep)[1:]:
            print('  __________________________________________________  ', line)
        print()
        print('  ____________________________________________________________________________ ')
        print(' |          |          |          |          |          |          |          |')
        print(' |          |          |          |          |          |          |          |')
        print(' | Sunday   | Monday   | Tuesday  | Wednesday| Thursday | Friday   | Saturday |')
        print(' |          |          |          |          |          |          |          |')
        print(' |__________|__________|__________|__________|__________|__________|__________|')
        for week in calendar.Calendar(6).monthdays2calendar(year, month):
            print(' |          |          |          |          |          |          |          |')
            line = ''
            for day in week:
                if day[0] == 0:
                    line += ' |         '
                else:
                    line += ' | ' + str(day[0]).ljust(8)
            line += ' |'
            print(line)
            for _ in range(5):
                print(' |' + 7*'          |')
            print(' |' + 7*'__________|')

    @staticmethod
    def _short(year, month):
        if month == 0:
            print(calendar.TextCalendar(6).formatyear(year))
        else:
            print(calendar.TextCalendar(6).formatmonth(year, month))

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()

        if options.get_long_flag():
            cls._long(options.get_year(), options.get_month())
        else:
            cls._short(options.get_year(), options.get_month())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
