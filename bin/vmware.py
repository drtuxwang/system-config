#!/usr/bin/env python3
"""
VMware Player launcher
"""

import os
import signal
import sys
from pathlib import Path
from typing import BinaryIO, List, TextIO, Union

from command_mod import Command
from subtask_mod import Background


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

    def get_vmplayer(self) -> Command:
        """
        Return vmplayer Command class object.
        """
        return self._vmplayer

    @staticmethod
    def _config() -> None:
        home = Path.home()
        path = Path(home, '.vmware', 'config')
        ofile: Union[BinaryIO, TextIO]

        if path.is_file():
            try:
                with path.open(errors='replace') as ifile:
                    configdata = ifile.readlines()
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot read '
                    f'"{path}" configuration file.',
                ) from exception
            if 'xkeymap.nokeycodeMap = true\n' in configdata:
                ifile.close()
                return
            try:
                with path.open('a', errors='replace') as ofile:
                    print("xkeymap.nokeycodeMap = true", file=ofile)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot modify '
                    f'"{path}" configuration file.',
                ) from exception
        else:
            if not path.parent.is_dir():
                try:
                    path.parent.mkdir()
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot create '
                        f'"{path.parent}" directory.',
                    ) from exception
            try:
                with path.open('w') as ofile:
                    print("xkeymap.nokeycodeMap = true", file=ofile)
            except OSError as exception:
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot create '
                    f'"{path}" configuration file.',
                ) from exception

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._vmplayer = Command('vmplayer', args=args[1:], errors='stop')
        self._pattern = ': Gtk-WARNING |: g_bookmark_file_get_size|^Fontconfig'
        self._config()


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

        Background(
            options.get_vmplayer().get_cmdline()
        ).run(pattern=options.get_pattern())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
