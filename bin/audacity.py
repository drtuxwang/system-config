#!/usr/bin/env python3
"""
Sandbox for "audacity" launcher
"""

import getpass
import glob
import os
import signal
import sys

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
    def _config() -> None:
        home = os.environ.get('HOME', '')
        audacitydir = os.path.join(home, '.audacity-data')
        if not os.path.isdir(audacitydir):
            try:
                os.mkdir(audacitydir)
            except OSError:
                pass
            else:
                if not os.path.isfile(
                        os.path.join(audacitydir, 'audacity.cfg')
                ):
                    with open(
                        os.path.join(audacitydir, 'audacity.cfg'),
                        'w',
                        encoding='utf-8',
                        newline='\n',
                    ) as ofile:
                        print("[AudioIO]", file=ofile)
                        print("PlaybackDevice=ALSA: pulse", file=ofile)
                        print("RecordingDevice=ALSA: pulse", file=ofile)

    def run(self) -> int:
        """
        Start program
        """
        audacity = network_mod.Sandbox('audacity', errors='stop')
        audacity.set_args(sys.argv[1:])

        if os.path.isfile(audacity.get_file() + '.py'):
            subtask_mod.Exec(audacity.get_cmdline()).run()

        work_dir = os.environ['PWD']  # "os.getcwd()" returns realpath instead
        if work_dir == os.environ['HOME']:
            desktop = os.path.join(work_dir, 'Desktop')
            if os.path.isdir(desktop):
                os.chdir(desktop)
                work_dir = desktop
        configs = [
            f'/tmp/{getpass.getuser()}:/var/tmp',
            f'/run/user/{os.getuid()}/pulse',
            os.path.join(os.getenv('HOME', '/'), '.config/ibus'),
            os.path.join(os.getenv('HOME', '/'), '.audacity-data'),
            work_dir,
        ]
        if len(sys.argv) >= 2:
            if os.path.isdir(sys.argv[1]):
                configs.append(os.path.abspath(sys.argv[1]))
            elif os.path.isfile(sys.argv[1]):
                configs.append(os.path.dirname(os.path.abspath(sys.argv[1])))
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
