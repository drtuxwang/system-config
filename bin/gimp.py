#!/usr/bin/env python3
"""
Wrapper for "gimp" command

Use '-reset' to remove profile
"""

import shutil
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command, Platform
from subtask_mod import Background, Exec


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

    def get_gimp(self) -> Command:
        """
        Return gimp Command class object.
        """
        return self._gimp

    @staticmethod
    def _reset() -> None:
        config_path = Path(Path.home(), '.config', 'GIMP')
        if config_path.is_dir():
            for path in [Path(config_path, x) for x in config_path.iterdir()]:
                if path.is_dir():
                    print(f'Removing "{path}"...')
                    shutil.rmtree(path)
                    path.mkdir()
                    with Path(path, 'gimprc').open('w') as ofile:
                        print('(theme "Light")', file=ofile)
                        print('(icon-size medium)', file=ofile)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        pathextra = (
            ['/Applications/GIMP-2.10.app/Contents/MacOS']
            if Platform.get_system() == 'macos' else []
        )

        self._gimp = Command('gimp', pathextra=pathextra, errors='stop')
        if len(args) > 1:
            if args[1] == '-reset':
                self._reset()
                raise SystemExit(0)
            if args[1] in ('-v', '-V', '-version', '--version'):
                self._gimp.set_args(['--version'])
                Exec(self._gimp.get_cmdline()).run()

        self._gimp.set_args(['--no-splash'] + args[1:])
        self._pattern = (
            '^$| GLib-WARNING | GLib-GObject-WARNING | Gtk-WARNING |: Gimp-|'
            ' g_bookmark_file_get_size:|recently-used.xbel|^ sRGB |^lcms: |'
            'pixmap_path: |in <module>| import |wrong ELF class:|'
            ': LibGimpBase-WARNING |^Traceback |: undefined symbol:|'
            ' XMP metadata:|: No XMP packet found|: GEGL-gegl-operation.c|'
            ': using babl for|gimp_pickable_contiguous_region_by_seed:|'
            'librsvg-WARNING|Plug-in| deprecated |GIMP is started|'
            'machine-id: |GIMP-Message: |- /Applications/|'
            'gimp_check_updates_callback: |GLib-GObject-CRITICAL |'
            'GIMP-Error: |Please create the folder|GeglBuffer|using gegl copy|'
            'gegl_tile_cache_destroy:|Failed to parse tag cache:'
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

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        options = Options()

        Background(
           options.get_gimp().get_cmdline()
        ).run(pattern=options.get_pattern())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
