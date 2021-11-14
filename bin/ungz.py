#!/usr/bin/env python3
"""
Uncompress a file in GZIP format.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

import command_mod
import file_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_archives(self) -> List[str]:
        """
        Return archive files.
        """
        return self._args.archives

    def get_command(self) -> command_mod.Command:
        """
        Return gzip Command class object.
        """
        return self._command

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Uncompress a file in GZIP format.",
        )

        parser.add_argument(
            'archives',
            nargs='+',
            metavar='file.gz',
            help="Archive file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._command = command_mod.Command('gzip', errors='stop')
        self._command.set_args(['-d', '--stdout'])


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

        cmdline = options.get_command().get_cmdline()
        for file in options.get_archives():
            if file.endswith('.gz') and os.path.isfile(file):
                print(f"{file}:")

                output = os.path.basename(file)[:-3]
                task = subtask_mod.Batch(cmdline + [file])
                task.run(file=output)
                if task.get_exitcode():
                    for line in task.get_error():
                        print(line, file=sys.stderr)
                    raise SystemExit(1)

                file_stat = file_mod.FileStat(file)
                os.chmod(output, file_stat.get_mode())
                file_time = file_stat.get_time()
                os.utime(output, (file_time, file_time))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
