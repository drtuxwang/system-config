#!/usr/bin/env python3
"""
Sandbox for ET Wolf launcher
"""

import glob
import os
import shutil
import signal
import sys
from pathlib import Path
from typing import Any

from command_mod import Command
from file_mod import FileUtil
from network_mod import Sandbox
from subtask_mod import Daemon, Exec


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
        if sys.version_info < (3, 9):
            def _readlink(file: Any) -> Path:
                return Path(os.readlink(file))
            Path.readlink = _readlink  # type: ignore

    def _punkbuster(self) -> None:
        path = Path(Path.home(), '.etwolf', 'pb')
        link_path = Path(Path(self._command.get_file()).parent, 'pb')
        if not path.is_symlink():
            if path.is_dir():
                try:
                    shutil.rmtree(path)
                except OSError:
                    return
            # pylint: disable=no-member
        elif path.readlink() != link_path:  # type: ignore
            # pylint: enable=no-member
            path.unlink()
        if not path.is_symlink():
            try:
                path.symlink_to(link_path)
            except OSError:
                pass
        if not os.access(Path(path, 'pbcl.so'), os.R_OK):
            raise SystemExit(
                f'{sys.argv[0]}: Cannot access "pbcl.so" in '
                f'"{path}" directory.',
            )
        path = Path(Path.home(), '.etwolf', 'etmain', 'etkey')
        if not path.is_file():
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find '
                f'"{path}" key file (see http://www.etkey.net).',
            )

    def _config(self) -> None:
        os.chdir(Path(self._command.get_file()).parent)
        os.environ['SDL_AUDIODRIVER'] = 'pulse'
        etsdl = (
            glob.glob('/usr/lib/i386-linux-gnu/libSDL-*so*') +
            glob.glob('/usr/lib32/libSDL-*so*') +
            glob.glob('/usr/lib/libSDL-*so*')
        )
        if not etsdl:
            raise SystemExit(
                f"{sys.argv[0]}: Cannot find SDL sound interface library.",
            )
        os.environ['ETSDL_SDL_LIB'] = etsdl[0]
        if 'LD_PRELOAD' in os.environ:
            os.environ['LD_PRELOAD'] = (
                f"{os.environ['LD_PRELOAD']}{os.pathsep}"
                f"{Path(os.getcwd(), 'et-sdl-sound-r29', 'et-sdl-sound.so')}"
            )
        else:
            os.environ['LD_PRELOAD'] = str(
                Path(os.getcwd(), 'et-sdl-sound-r29', 'et-sdl-sound.so')
            )
        path = Path(Path.home(), '.etwolf')
        if not path.is_dir():
            path.mkdir()

    def run(self) -> int:
        """
        Start program
        """
        self._command = Sandbox('et.x86', errors='ignore')
        if not Path(self._command.get_file()).is_file():
            command = Command('et', args=sys.argv[1:], errors='stop')
            Exec(command.get_cmdline()).run()

        configs = [
            'net',
            f'/run/user/{os.getuid()}/pulse',
            f"{Path(Path.home(), '.etwolf')}",
        ]
        self._command.sandbox(configs)

        self._config()
        self._punkbuster()
        self._command.set_args(sys.argv[1:])

        log_path = Path(FileUtil.tmpdir(), 'et.log')
        Daemon(self._command.get_cmdline()).run(file=log_path)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
