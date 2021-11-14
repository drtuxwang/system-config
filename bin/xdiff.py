#!/usr/bin/env python3
"""
Graphical file comparison and merge tool.
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

    def get_pattern(self) -> str:
        """
        Return filter pattern.
        """
        return self._pattern

    def get_meld(self) -> command_mod.Command:
        """
        Return meld Command class object.
        """
        return self._meld

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Graphical file comparison and merge tool.",
        )

        parser.add_argument(
            'files',
            nargs=2,
            metavar='file',
            help="File to compare.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._meld = command_mod.Command('meld', errors='stop')
        files = self._args.files
        if os.path.isdir(files[0]) and os.path.isfile(files[1]):
            self._meld.set_args(
                [os.path.join(files[0], os.path.basename(files[1])), files[1]])
        elif os.path.isfile(files[0]) and os.path.isdir(files[1]):
            self._meld.set_args(
                [files[0], os.path.join(files[1], os.path.basename(files[0]))])
        elif os.path.isfile(files[0]) and os.path.isfile(files[1]):
            self._meld.set_args(args[1:])
        else:
            raise SystemExit(f"{sys.argv[0]}: Cannot compare two directories.")

        self._pattern = (
            '^$|: Gtk-WARNING |: GtkWarning: |: Gtk-CRITICAL |^  buttons =|'
            '^  gtk.main|recently-used.xbel|: Allocating size to GtkVBox |'
            ': dconf-CRITICAL'
        )


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

        task = subtask_mod.Task(options.get_meld().get_cmdline())
        task.run(pattern=options.get_pattern())
        return task.get_exitcode()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
