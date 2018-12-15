#!/usr/bin/env python3
"""
Check for missing sequence in numbered files.
"""

import argparse
import glob
import os
import signal
import sys


if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Check for missing sequence in numbered files.')

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='File to check.'
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
    def _check_missing(seq_name, numbers):
        sequence = set(range(min(numbers), max(numbers)+1))
        name, ext = seq_name
        for missing in sorted(sequence - numbers):
            print("Missing file in sequence: {0:s}_{1:02d}{2:s}".format(
                name,
                missing,
                ext
            ))

    @classmethod
    def _check_sequences(cls, files):
        sequences = {}
        for file in files:
            if '_' in file and os.path.isfile(file):
                name, ext = os.path.splitext(file)
                name, number = name.rsplit('_', 1)
                seq_name = (name, ext)
                sequences[seq_name] = sequences.get(seq_name, set())
                try:
                    sequences[seq_name].add(int(number))
                except ValueError:
                    pass
            elif os.path.isdir(file):
                cls._check_sequences(glob.glob(os.path.join(file, '*')))

        for seq_name, numbers in sorted(sequences.items()):
            if len(numbers) > 1:
                cls._check_missing(seq_name, numbers)

    @classmethod
    def run(cls):
        """
        Start program
        """
        options = Options()

        cls._check_sequences(options.get_files())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
