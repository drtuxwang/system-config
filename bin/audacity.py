#!/usr/bin/env python3
"""
Wrapper for "audacity" command
"""

import glob
import os
import signal
import sys

import command_mod
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
                    with open(os.path.join(audacitydir, 'audacity.cfg'),
                              'w', newline='\n') as ofile:
                        print("[AudioIO]", file=ofile)
                        print("PlaybackDevice=ALSA: pulse", file=ofile)
                        print("RecordingDevice=ALSA: pulse", file=ofile)

    def run(self) -> int:
        """
        Start program
        """
        audacity = command_mod.Command('audacity', errors='stop')
        audacity.set_args(sys.argv[1:])
        pattern = (
            '^$|^HCK OnTimer|: Gtk-WARNING | LIBDBUSMENU-GLIB-WARNING |'
            '^ALSA lib |alsa.c|^Cannot connect to server socket|'
            '^jack server|Debug: |^JackShmReadWrite|^[01]|^-1|^Cannot connect'
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
