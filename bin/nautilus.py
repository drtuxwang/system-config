#!/usr/bin/env python3
"""
Wrapper for "nautilus" command
"""

import os
import signal
import sys
from pathlib import Path
from typing import List

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

    def get_nautilus(self) -> Command:
        """
        Return nautilus Command class object.
        """
        return self._nautilus

    def _config(self) -> None:
        config_path = Path(Path.home(), '.local', 'share', 'applications')
        if not config_path.is_dir():
            try:
                config_path.mkdir(parents=True)
            except OSError:
                return
        path = Path(config_path, 'mimeapps.list')
        if not path.is_file():
            try:
                with path.open('w') as ofile:
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
            config_path,
            'application/vnd.oasis.opendocument.text',
            'soffice'
        )
        self._userapp(config_path, 'image/jpeg', 'gqview')
        self._userapp(config_path, 'text/html', 'xweb')

    @staticmethod
    def _userapp(config_path: Path, mime_type: str, app_name: str) -> None:
        path = Path(config_path, f'{app_name}-userapp.desktop')
        if not path.is_dir():
            try:
                with path.open('w') as ofile:
                    print("[Desktop Entry]", file=ofile)
                    print(f"Name={app_name}", file=ofile)
                    print(f"Exec={app_name}", ' %f', file=ofile)
                    print("Type=Application", file=ofile)
                    print("NoDisplay=true", file=ofile)
            except OSError:
                return

        path = Path(config_path, 'mimeinfo.cache')
        try:
            if not path.is_file():
                with path.open('w') as ofile:
                    print("[MIME Cache]", file=ofile)
            with path.open(errors='replace') as ifile:
                if f'{mime_type}={app_name}-userapp.desktop' in ifile:
                    return
            with path.open('a') as ofile:
                print(f"{mime_type}={app_name}-userapp.desktop", file=ofile)
        except OSError:
            return

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._nautilus = Command('nautilus', errors='stop')
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
            options.get_nautilus().get_cmdline()
        ).run(pattern=options.get_pattern())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
