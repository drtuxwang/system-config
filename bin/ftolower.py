#!/usr/bin/env python3
"""
Convert filename to lowercase.
"""

import argparse
import glob
import os
import shutil
import signal
import sys


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
            description='Convert filename to lowercase.')

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='File to change.'
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
    def run():
        """
        Start program
        """
        options = Options()

        for file in options.get_files():
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" file.')
            if os.sep not in file:
                newfile = file.lower()
            elif file.endswith(os.sep):
                newfile = os.path.join(
                    os.path.dirname(file), os.path.basename(file[:-1]).lower())
            else:
                newfile = os.path.join(
                    os.path.dirname(file), os.path.basename(file).lower())
            if newfile != file:
                print('Converting filename "' + file + '" to lowercase...')
                if os.path.isfile(newfile):
                    raise SystemExit(
                        sys.argv[0] + ': Cannot rename over existing "' +
                        newfile + '" file.'
                    )
                try:
                    shutil.move(file, newfile)
                except OSError as exception:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot rename "' + file +
                        '" file to "' + newfile + '".'
                    ) from exception


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
