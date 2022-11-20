#!/usr/bin/env python3
"""
Wrapper for "gimp" command
"""

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
        self.parse(sys.argv)

    def get_pattern(self) -> str:
        """
        Return filter pattern.
        """
        return self._pattern

    def get_gimp(self) -> command_mod.Command:
        """
        Return gimp Command class object.
        """
        return self._gimp

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._gimp = command_mod.Command('gimp', errors='stop')
        self._gimp.set_args(['--no-splash'] + args[1:])
        self._pattern = (
            '^$| GLib-WARNING | GLib-GObject-WARNING | Gtk-WARNING |: Gimp-|'
            ' g_bookmark_file_get_size:|recently-used.xbel|^ sRGB |^lcms: |'
            'pixmap_path: |in <module>| import |wrong ELF class:|'
            ': LibGimpBase-WARNING |^Traceback |: undefined symbol:|'
            ' XMP metadata:|: No XMP packet found|: GEGL-gegl-operation.c|'
            ': using babl for|gimp_pickable_contiguous_region_by_seed:|'
            'librsvg-WARNING|Plug-in| deprecated '
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

        subtask_mod.Background(options.get_gimp(
            ).get_cmdline()).run(pattern=options.get_pattern())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
