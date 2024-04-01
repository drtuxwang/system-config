#!/usr/bin/env python3
"""
Sandbox for "tenacity" launcher
"""

import getpass
import os
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

    @staticmethod
    def _config(audacity: Sandbox) -> Path:
        if Path(audacity.get_file()).name == 'tenacity':
            return Path(Path.home(), '.config', 'tenacity')

        audacitydir = Path(Path.home(), '.audacity-data')
        if not audacitydir.is_dir():
            try:
                os.mkdir(audacitydir)
            except OSError:
                pass
            else:
                path = Path(audacitydir, 'audacity.cfg')
                if not path.is_file():
                    with path.open('w') as ofile:
                        print("[AudioIO]", file=ofile)
                        print("PlaybackDevice=ALSA: pulse", file=ofile)
                        print("RecordingDevice=ALSA: pulse", file=ofile)
        return audacitydir

    @classmethod
    def run(cls) -> int:
        """
        Start program
        """
        audacity = Sandbox('tenacity', errors='ignore')
        if not audacity.is_found():
            audacity = Sandbox('audacity', errors='stop')
        if Path(f'{audacity.get_file()}.py').is_file():
            Exec(audacity.get_cmdline() + sys.argv[1:]).run()
        config_dir = cls._config(audacity)

        # "os.getcwd()" returns realpath instead
        work_dir = Path(os.environ['PWD'])
        if work_dir == Path.home():
            desktop = Path(work_dir, 'Desktop')
            if desktop.is_dir():
                os.chdir(desktop)
                work_dir = desktop

        configs = [
            f'/tmp/{getpass.getuser()}:/var/tmp',
            f'/run/user/{os.getuid()}/pulse',
            Path(Path.home(), '.config/ibus'),
            config_dir,
            work_dir,
        ]

        for arg in sys.argv[1:]:
            path = Path(arg).resolve()
            if arg == '-net':
                configs.append('net')
            elif path.is_dir():
                audacity.append_arg(path)
                configs.append(path)
            elif path.is_file():
                audacity.append_arg(path)
                configs.append(path.parent)
            else:
                audacity.append_arg(arg)

        audacity.sandbox(configs)

        pattern = (
            '^$|: (Gdk|GdkPixbuf|GLib-GObject)-|[.]so|: invalid (image|bitmap)'
        )

        cmdline = audacity.get_cmdline()
        Background(cmdline).run(pattern=pattern)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
