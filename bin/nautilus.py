#!/usr/bin/env python3
"""
Wrapper for "nautilus" command
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

    def get_nautilus(self) -> command_mod.Command:
        """
        Return nautilus Command class object.
        """
        return self._nautilus

    def _config(self) -> None:
        home = os.environ.get('HOME', '')
        configdir = os.path.join(home, '.local', 'share', 'applications')
        if not os.path.isdir(configdir):
            try:
                os.makedirs(configdir)
            except OSError:
                return
        file = os.path.join(configdir, 'mimeapps.list')
        if not os.path.isfile(file):
            try:
                with open(file, 'w', encoding='utf-8', newline='\n') as ofile:
                    print("[Added Associations]", file=ofile)
                    print("audio/ac3=vlc.desktop;", file=ofile)
                    print("audio/mp4=vlc.desktop;", file=ofile)
                    print("audio/mpeg=vlc.desktop;", file=ofile)
                    print(
                        "audio/vnd.rn-realaudio=vlc.desktop;", file=ofile)
                    print("audio/vorbis=vlc.desktop;", file=ofile)
                    print("audio/x-adpcm=vlc.desktop;", file=ofile)
                    print("audio/x-matroska=vlc.desktop;", file=ofile)
                    print("audio/x-mpegurl=vlc.desktop;", file=ofile)
                    print("audio/x-mp2=vlc.desktop;", file=ofile)
                    print("audio/x-mp3=vlc.desktop;", file=ofile)
                    print("audio/x-ms-wma=vlc.desktop;", file=ofile)
                    print("audio/x-scpls=vlc.desktop;", file=ofile)
                    print("audio/x-vorbis=vlc.desktop;", file=ofile)
                    print("audio/x-wav=vlc.desktop;", file=ofile)
                    print("image/jpeg=gqview.desktop;", file=ofile)
                    print("video/avi=vlc.desktop;", file=ofile)
                    print("video/mp4=vlc.desktop;", file=ofile)
                    print("video/mpeg=vlc.desktop;", file=ofile)
                    print("video/quicktime=vlc.desktop;", file=ofile)
                    print(
                        "video/vnd.rn-realvideo=vlc.desktop;", file=ofile)
                    print("video/x-matroska=vlc.desktop;", file=ofile)
                    print("video/x-ms-asf=vlc.desktop;", file=ofile)
                    print("video/x-msvideo=vlc.desktop;", file=ofile)
                    print("video/x-ms-wmv=vlc.desktop;", file=ofile)
                    print("video/x-ogm=vlc.desktop;", file=ofile)
                    print("video/x-theora=vlc.desktop;", file=ofile)
                    print(
                        '\n# xdg-open (ie "xdg-mime default vlc.desktop '
                        'x-scheme-handler/rtsp"', file=ofile
                    )
                    print("[Default Applications]", file=ofile)
                    print("x-scheme-handler/mms=vlc.desktop", file=ofile)
                    print("x-scheme-handler/mms=vlc.desktop", file=ofile)
                    print("x-scheme-handler/rtsp=vlc.desktop", file=ofile)
            except OSError:
                return
        self._userapp(
            configdir,
            'application/vnd.oasis.opendocument.text',
            'soffice'
        )
        self._userapp(configdir, 'image/jpeg', 'gqview')
        self._userapp(configdir, 'text/html', 'xweb')

    @staticmethod
    def _userapp(configdir: str, mime_type: str, app_name: str) -> None:
        file = os.path.join(configdir, app_name + '-userapp.desktop')
        if not os.path.isfile(file):
            try:
                with open(file, 'w', encoding='utf-8', newline='\n') as ofile:
                    print("[Desktop Entry]", file=ofile)
                    print(f"Name={app_name}", file=ofile)
                    print(f"Exec={app_name}", ' %f', file=ofile)
                    print("Type=Application", file=ofile)
                    print("NoDisplay=true", file=ofile)
            except OSError:
                return

        file = os.path.join(configdir, 'mimeinfo.cache')
        try:
            if not os.path.isfile(file):
                with open(file, 'w', encoding='utf-8', newline='\n') as ofile:
                    print("[MIME Cache]", file=ofile)
            with open(file, encoding='utf-8', errors='replace') as ifile:
                if f'{mime_type}={app_name}-userapp.desktop' in ifile:
                    return
            with open(file, 'a', encoding='utf-8', newline='\n') as ofile:
                print(f"{mime_type}={app_name}-userapp.desktop", file=ofile)
        except OSError:
            return

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._nautilus = command_mod.Command('nautilus', errors='stop')
        if len(args) == 1:
            if 'DESKTOP_STARTUP_ID' not in os.environ:
                self._nautilus.set_args([os.getcwd()])
        else:
            self._nautilus.set_args(args[1:])
        self._pattern = (
            '^$|^Initializing nautilus|: Gtk-WARNING |: Gtk-CRITICAL | '
            'GLib.*CRITICAL |^Shutting down'
        )
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

        subtask_mod.Background(options.get_nautilus().get_cmdline()).run(
            pattern=options.get_pattern())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
