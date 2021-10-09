#!/usr/bin/env python3
"""
Create wrapper to run script/executable.
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

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description='Create wrapper to run script/executable.',
        )

        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='Script/executable to wrap.'
        )

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
    def _create(file: str, link: str) -> None:
        try:
            with open(link, 'w', encoding='utf-8', newline='\n') as ofile:
                print("#!/usr/bin/env bash", file=ofile)
                print("#", file=ofile)
                print("# fwrapper.py generated script", file=ofile)
                print("#\n", file=ofile)
                print('MYDIR=$(dirname "$0")', file=ofile)
                if file == os.path.abspath(file):
                    directory = os.path.dirname(file)
                    print(
                        'PATH=$(echo "$PATH" | sed -e "s@$MYDIR@' +
                        directory + '@")',
                        file=ofile
                    )
                    print("export PATH\n", file=ofile)
                    print('exec "' + file + '" "$@"', file=ofile)
                else:
                    print('exec "$MYDIR/' + file + '" "$@"', file=ofile)

            os.chmod(link, int('755', 8))
            file_time = os.path.getmtime(file)
            os.utime(link, (file_time, file_time))
        except OSError as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + link + '" wrapper file.'
            ) from exception

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        self._files = options.get_files()
        for file in self._files:
            if not os.path.isfile(file):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + file + '" file.')

            link = os.path.basename(file)
            if os.path.exists(link):
                print('Updating "{0:s}" wrapper for "{1:s}"...'.format(
                    link, file))
            else:
                print('Creating "{0:s}" wrapper for "{1:s}"...'.format(
                    link, file))
            self._create(file, link)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
