#!/usr/bin/env python3
"""
Sandbox for "audacity" launcher
"""

import getpass
import os
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
        if os.linesep != '\n':
            def _open(file, *args, **kwargs):  # type: ignore
                if 'newline' not in kwargs and args and 'b' not in args[0]:
                    kwargs['newline'] = '\n'
                return open(str(file), *args, **kwargs)
            Path.open = _open  # type: ignore

    @staticmethod
    def _config() -> None:
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

    def run(self) -> int:
        """
        Start program
        """
        audacity = network_mod.Sandbox('audacity', errors='stop')
        audacity.set_args(sys.argv[1:])

        if Path(f'{audacity.get_file()}.py').is_file():
            subtask_mod.Exec(audacity.get_cmdline()).run()

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
            Path(Path.home(), '.audacity-data'),
            work_dir,
        ]
        if len(sys.argv) >= 2:
            if Path(sys.argv[1]).is_dir():
                configs.append(Path(sys.argv[1]).resolve())
            elif Path(sys.argv[1]).is_file():
                configs.append(Path(sys.argv[1]).resolve().parent)
            if sys.argv[1] == '-net':
                audacity.set_args(sys.argv[2:])
                configs.append('net')
        audacity.sandbox(configs)

        pattern = (
            '^$|^HCK OnTimer|: Gtk-WARNING | LIBDBUSMENU-GLIB-WARNING |'
            '^ALSA lib |alsa.c|^Cannot connect to server socket|'
            '^jack server|Debug: |^JackShmReadWrite|^[01]|^-1|^Cannot connect|'
            ': no version info'
        )
        self._config()

        cmdline = audacity.get_cmdline()
        subtask_mod.Background(cmdline).run(pattern=pattern)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
