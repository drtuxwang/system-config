#!/usr/bin/env python3
"""
Check JPEG picture files.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_directories(self) -> List[str]:
        """
        Return list of directories.
        """
        return self._args.directories

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Check JPEG picture files.",
        )

        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help="Directory containing JPEG files to check.",
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
    def run() -> int:
        """
        Start program
        """
        options = Options()
        directories = options.get_directories()

        errors = []
        jpeginfo = command_mod.Command(
            'jpeginfo',
            args=['--info', '--check'],
            errors='stop'
        )
        for directory in directories:
            if os.path.isdir(directory):
                files = []
                for file in glob.glob(os.path.join(directory, '*.*')):
                    if os.path.splitext(file)[1].lower() in ('.jpg', '.jpeg'):
                        files.append(file)
                if files:
                    task = subtask_mod.Batch(jpeginfo.get_cmdline() + files)
                    task.run()
                    for line in task.get_output():
                        if '[ERROR]' in line:
                            errors.append(line)
                        else:
                            print(line)
        if errors:
            for line in errors:
                print(line)
            raise SystemExit(f"Total errors encountered: {len(errors)}.")

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
