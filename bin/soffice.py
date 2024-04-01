#!/usr/bin/env python3
"""
Sandbox for "soffice" launcher
"""

import glob
import os
import shutil
import signal
import sys
from pathlib import Path

from network_mod import Sandbox
from subtask_mod import Background, Exec


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

    def _config(self) -> None:
        for file in glob.glob('.~lock.*#'):  # Remove stupid lock files
            try:
                os.remove(file)
            except OSError:
                pass
        home = Path.home()
        for path in home.glob(
            '.config/libreoffice/*/user/egistrymodifications.xcu'
        ):
            if path.is_file():
                try:
                    path.unlink()
                    path.mkdir()
                except OSError:
                    pass

        # Remove insecure macros scripting
        try:
            shutil.rmtree(Path(
                Path(self._soffice.get_file()).parents[1],
                'share',
                'Scripts',
            ))
        except OSError:
            pass

        # Disable update nagging
        for path in Path(self._soffice.get_file()).parent.glob('libupd*.so'):
            try:
                os.remove(path)
            except OSError:
                pass

    @staticmethod
    def _setenv() -> None:
        if 'GTK_MODULES' in os.environ:
            # Fix Linux 'gnomebreakpad' problems
            del os.environ['GTK_MODULES']

    def run(self) -> int:
        """
        Start program
        """
        self._soffice = Sandbox(
            Path('program', 'soffice'),
            args=['--nologo'],
            errors='stop',
        )
        if (
            Path(f'{self._soffice.get_file()}.py').is_file() or
            sys.argv[1:] == ['--version']
        ):
            Exec(self._soffice.get_cmdline() + sys.argv[1:]).run()

        work_dir = os.environ['PWD']  # "os.getcwd()" returns realpath instead
        home = str(Path.home())
        if work_dir == home:
            desktop = Path(work_dir, 'Desktop')
            if desktop.is_dir():
                os.chdir(desktop)
                work_dir = str(desktop)

        configs = [
            '/tmp',
            f'/run/user/{os.getuid()}',
            Path(home, '.config/ibus'),
            Path(home, '.config/libreoffice'),
            work_dir,
        ]

        for arg in sys.argv[1:]:
            path = Path(arg).resolve()
            if arg == '-net':
                configs.append('net')
            elif path.is_dir():
                self._soffice.append_arg(path)
                configs.append(path)
            elif path.is_file():
                self._soffice.append_arg(path)
                configs.append(path.parent)
            else:
                self._soffice.append_arg(arg)

        self._soffice.sandbox(configs)

        self._pattern = (
            '^$|: GLib-CRITICAL |: GLib-GObject-WARNING |: G[dt]k-WARNING |'
            ': wrong ELF class:|: Could not find a Java Runtime|'
            ': failed to read path from javaldx|^Failed to load module:|'
            'unary operator expected|: unable to get gail version number|'
            'gtk printer|: GConf-WARNING|: Connection refused|GConf warning: '
            '|GConf Error: |: invalid source position|:'
        )
        self._config()
        self._setenv()

        cmdline = self._soffice.get_cmdline()
        Background(cmdline).run(pattern=self._pattern)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
