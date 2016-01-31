#!/usr/bin/env python3
"""
Print large monthly calendar.
"""

import argparse
import calendar
import glob
import os
import signal
import sys

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_month(self):
        """
        Return month of files.
        """
        return self._args.month[0]

    def get_year(self):
        """
        Return year of files.
        """
        return self._args.year[0]

    def _parse_args(self, args):
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

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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

        print('\n                  [ ', calendar.month_name[options.get_month()] + ' ',
              options.get_year(), ' ]\n')
        for line in calendar.TextCalendar(6).formatmonth(
                options.get_year(), options.get_month()).split(os.linesep)[1:]:
            print('  __________________________________________________  ', line)
        print()
        print('  ____________________________________________________________________________ ')
        print(' |          |          |          |          |          |          |          |')
        print(' |          |          |          |          |          |          |          |')
        print(' | Sunday   | Monday   | Tuesday  | Wednesday| Thursday | Friday   | Saturday |')
        print(' |          |          |          |          |          |          |          |')
        print(' |__________|__________|__________|__________|__________|__________|__________|')
        for week in calendar.Calendar(6).monthdays2calendar(
                options.get_year(), options.get_month()):
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


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
