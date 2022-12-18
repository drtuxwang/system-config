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

import network_mod
import subtask_mod


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
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

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
        self._soffice = network_mod.Sandbox(
            Path('program', 'soffice'),
            errors='stop'
        )
        self._soffice.set_args(['--nologo'] + sys.argv[1:])
        if Path(f'{self._soffice.get_file()}.py').is_file():
            subtask_mod.Exec(self._soffice.get_cmdline()).run()
        if sys.argv[1:] == ['--version']:
            subtask_mod.Exec(self._soffice.get_cmdline()).run()

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
        if len(sys.argv) >= 2:
            if Path(sys.argv[1]).is_dir():
                configs.append(Path(sys.argv[1]).resolve())
            elif Path(sys.argv[1]).is_file():
                configs.append(Path(sys.argv[1]).resolve().parent)
            if sys.argv[1] == '-net':
                self._soffice.set_args(['--nologo'] + sys.argv[2:])
                configs.append('net')
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
        subtask_mod.Background(cmdline).run(pattern=self._pattern)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
