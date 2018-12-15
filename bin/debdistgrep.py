#!/usr/bin/env python3
"""
Print lines matching a pattern in Debian package file.
"""

import argparse
import glob
import json
import os
import re
import signal
import sys

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_packages_file(self):
        """
        Return packages file location.
        """
        return self._args.packages_file[0]

    def get_patterns(self):
        """
        Return list of regular expression search patterns.
        """
        return self._args.patterns

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Print lines matching a pattern in Debian '
            'package file.'
        )

        parser.add_argument(
            'packages_file',
            nargs=1,
            metavar='distribution.json',
            help='Debian package file.'
        )
        parser.add_argument(
            'patterns',
            nargs='+',
            metavar='pattern',
            help='Regular expression.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Main:
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            self._packages = {}
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def _read_data(file):
        try:
            with open(file) as ifile:
                data = json.load(ifile)
        except (OSError, json.decoder.JSONDecodeError):
            raise SystemExit(
                sys.argv[0] + ': Cannot read "' + file + '" json file.'
            )

        return data

    @classmethod
    def _read_distribution_lines(cls, packages_file):
        distribution_data = cls._read_data(packages_file)
        lines = []
        for url in distribution_data['urls']:
            lines.extend(distribution_data['data'][url]['text'])

        return lines

    @staticmethod
    def _search_distribution_packages(lines, patterns):
        for pattern in patterns:
            ispattern = re.compile(pattern, re.IGNORECASE)
            for line in lines:
                if ispattern.search(line):
                    print(line)

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

    def run(self):
        """
        Start program
        """
        options = Options()

        lines = self._read_distribution_lines(options.get_packages_file())
        self._search_distribution_packages(lines, options.get_patterns())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
