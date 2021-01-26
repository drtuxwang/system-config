#!/usr/bin/env python3
"""
Decode URL query strings.
"""

import argparse
import glob
import os
import signal
import sys
import urllib.parse


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_urls(self):
        """
        Return list of URLs.
        """
        return self._args.urls

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Decode URL query strings.'
        )

        parser.add_argument(
            'urls',
            nargs='+',
            metavar='url',
            help='URL query string.',
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
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)
        sys.exit(0)

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

        for url in options.get_urls():
            print(urllib.parse.unquote(url))


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
