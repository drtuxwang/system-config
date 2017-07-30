#!/usr/bin/env python3
"""
Displays month or year calendar.
"""

import argparse
import calendar
import datetime
import glob
import os
import signal
import sys


if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


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
        parser = argparse.ArgumentParser(
            description='Displays month or year calendar.')

        parser.add_argument(
            '-l',
            dest='long_flag',
            action='store_true',
            help='Select long output.'
        )
        parser.add_argument(
            'month',
            nargs='?',
            type=int,
            help='Select month (1-12 or 0 for year.'
        )
        parser.add_argument(
            'year',
            nargs='?',
            type=int,
            help='Select year (2-9999).'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        now = datetime.datetime.now()
        self._year = now.year
        self._month = now.month
        if self._args.year:
            self._year = self._args.year
            if self._year < 2 or self._year > 9999:
                raise SystemExit(
                    sys.argv[0] + ': Invalid "' + str(self._year) +
                    '" year. Use 2-9999.'
                )
            self._month = self._args.month
            if self._month < 0 or self._month > 12:
                raise SystemExit(
                    sys.argv[0] + ': Invalid "' + str(self._month) +
                    '" month. Use 1-12 or 0 for year.'
                )
        elif self._args.month:
            self._month = self._args.month
            if self._month < 0 or self._month > 9999:
                raise SystemExit(
                    sys.argv[0] + ': Invalid "' + str(self._month) +
                    '" month or year. Use 1-12 for month or 13-9999 for year.'
                )
            elif self._month > 12:
                self._year = self._month
                self._month = 0
            elif self._month < now.month:
                self._year += 1  # Next year


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
        print(
            "\n" + " "*18 +
            "[ ", calendar.month_name[month] + " ", year, " ]\n"
        )
        for line in calendar.TextCalendar(6).formatmonth(
                year, month).split(os.linesep)[1:]:
            print("  " + "_"*51 + "  ", line)
        print()
        print("  " + "_"*76 + "  ")
        print(" " + ("|"+" "*10)*7 + "| ")
        print(" " + ("|"+" "*10)*7 + "| ")
        print(
            " | Sunday   | Monday   | Tuesday  | Wednesday| Thursday"
            " | Friday   | Saturday |"
        )
        print(" " + ("|"+" "*10)*7 + "| ")
        print(" " + ("|"+"_"*10)*7 + "| ")
        for week in calendar.Calendar(6).monthdays2calendar(year, month):
            print(" " + ("|"+" "*10)*7 + "| ")
            line = ''
            for day in week:
                if day[0] == 0:
                    line += ' |' + ' '*9
                else:
                    line += ' | ' + str(day[0]).ljust(8)
            line += ' |'
            print(line)
            for _ in range(5):
                print(" " + ("|"+" "*10)*7 + "| ")
            print(" " + ("|"+"_"*10)*7 + "| ")

    @staticmethod
    def _short(year, month):
        if month == 1:
            data = calendar.TextCalendar(6).formatmonth(year-1, 12)
        else:
            data = calendar.TextCalendar(6).formatmonth(year, month-1)
        last_month = data.split('\n')+['']

        data = calendar.TextCalendar(6).formatmonth(year, month)
        current_month = data.split('\n')+['']

        if month == 12:
            data = calendar.TextCalendar(6).formatmonth(year+1, 1)
        else:
            data = calendar.TextCalendar(6).formatmonth(year, month+1)
        next_month = data.split('\n')+['']

        for index in range(8):
            print("  {0:20s}   {1:20s}   {2:20s}".format(
                last_month[index],
                current_month[index],
                next_month[index]
            ))

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()

        month = options.get_month()
        if options.get_long_flag() or month == 0:
            cls._long(options.get_year(), month)
        else:
            cls._short(options.get_year(), month)


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
