#!/usr/bin/env python3
"""
Print arguments with first letter in upper case (camel case).
"""

import argparse
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

    def get_words(self) -> List[str]:
        """
        Return list of words.
        """
        return self._args.words

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Print arguments wth first letter in upper case.',
        )

        parser.add_argument('words', nargs='+', metavar='word', help='A word.')

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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
        sys.exit(0)

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
    def run() -> int:
        """
        Start program
        """
        options = Options()

        words = options.get_words()
        cwords = []
        for word in words:
            cparts = []
            for part in word.split('-'):
                cparts.append(part[:1].upper() + part[1:].lower())
            cwords.append('-'.join(cparts))
        print(" ".join(cwords))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
