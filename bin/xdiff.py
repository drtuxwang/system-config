#!/usr/bin/env python3
"""
Graphical file comparison and merge tool.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
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
        paths = [Path(x) for x in self._args.files]
        if paths[0].is_dir() and paths[1].is_file():
            self._meld.set_args(
                [Path(paths[0], Path(paths[1]).name, paths[1])],
            )
        elif Path(paths[0]).is_file() and Path(paths[1]).is_dir():
            self._meld.set_args(
                [paths[0], Path(paths[1], Path(paths[0]).name)],
            )
        elif Path(paths[0]).is_file() and Path(paths[1]).is_file():
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
            sys.exit(exception)  # type: ignore

    @staticmethod
    def config() -> None:
        """
        Configure program
        """
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

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
