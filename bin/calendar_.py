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
from typing import List


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_long_flag(self) -> bool:
        """
        Return long flag.
        """
        return self._args.long_flag

    def get_month(self) -> int:
        """
        Return month of files.
        """
        return self._month

    def get_year(self) -> int:
        """
        Return year of files.
        """
        return self._year

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Displays month or year calendar.",
        )

        parser.add_argument(
            '-l',
            dest='long_flag',
            action='store_true',
            help="Select long output.",
        )
        parser.add_argument(
            'month',
            nargs='?',
            type=int,
            help="Select month (1-12) or 0 for year.",
        )
        parser.add_argument(
            'year',
            nargs='?',
            type=int,
            help="Select year (2-9999).",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        now = datetime.datetime.now()
        self._year = now.year
        self._month = now.month
        if self._args.month:
            self._month = self._args.month
            if self._month < 0 or self._month > 12:
                raise SystemExit(
                    f'{sys.argv[0]}: Invalid "{self._month}" month. Use 1-12.',
                )
            if self._args.year:
                self._year = self._args.year
                if self._year < 2 or self._year > 9999:
                    raise SystemExit(
                        f'{sys.argv[0]}: Invalid '
                        f'"{self._year}" year. Use 2-9999.',
                    )
            elif self._month < now.month:
                self._year += 1  # Next year


class Main:
    """
    Main class
    """

    def __init__(self) -> None:
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config() -> None:
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
    def _long(year: int, month: int) -> None:
        print(
            f"\n{' '*18}[  {calendar.month_name[month]}  {year}  ]\n"
        )
        for line in calendar.TextCalendar(6).formatmonth(
                year, month).split(os.linesep)[1:]:
            print(f"  {'_'*51}  ", line)
        print()
        print(f"  {'_'*76}  ")
        print(f" {('|'+' '*10)*7}| ")
        print(f" {('|'+' '*10)*7}| ")
        print(
            " | Sunday   | Monday   | Tuesday  | Wednesday| Thursday"
            " | Friday   | Saturday |"
        )
        print(f" {('|'+' '*10)*7}| ")
        print(f" {('|'+'_'*10)*7}| ")
        for week in calendar.Calendar(6).monthdays2calendar(year, month):
            print(f" {('|'+' '*10)*7}| ")
            line = ''
            for day in week:
                if day[0] == 0:
                    line += ' |' + ' '*9
                else:
                    line += ' | ' + str(day[0]).ljust(8)
            line += ' |'
            print(line)
            for _ in range(5):
                print(f" {('|'+' '*10)*7}| ")
            print(f" {('|'+'_'*10)*7}| ")
        print()

    @staticmethod
    def _short(year: int, month: int) -> None:
        if month == 1:
            data = calendar.TextCalendar(6).formatmonth(year-1, 12)
        else:
            data = calendar.TextCalendar(6).formatmonth(year, month-1)
        last_month = data.splitlines()+['']

        data = calendar.TextCalendar(6).formatmonth(year, month)
        current_month = data.splitlines()+['']

        if month == 12:
            data = calendar.TextCalendar(6).formatmonth(year+1, 1)
        else:
            data = calendar.TextCalendar(6).formatmonth(year, month+1)
        next_month = data.splitlines()+['']

        for index in range(8):
            print(
                f"  {last_month[index]:20s}   "
                f"{current_month[index]:20s}   "
                f"{next_month[index]:20s}",
            )

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        options = Options()

        month = options.get_month()
        if options.get_long_flag() or month == 0:
            cls._long(options.get_year(), month)
        else:
            cls._short(options.get_year(), month)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
