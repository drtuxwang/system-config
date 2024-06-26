#!/usr/bin/env python3
"""
Wrapper for Linux/Mac screen locking
"""

import os
import signal
import sys
import time
from pathlib import Path

from command_mod import Command
from desktop_mod import Desktop
from subtask_mod import Background
from task_mod import Tasks


class ScreenLocker:
    """
    Screen Locker base class.
    """

    def __init__(self) -> None:
        self._daemon: Command = None
        self._command: Command = None
        self._setup()

    def _setup(self) -> None:
        pass

    def detect(self) -> bool:
        """
        Return True if installed.
        """
        return self._command.is_found()

    @staticmethod
    def factory(desktop: str) -> 'ScreenLocker':
        """
        Return ScreenLocker sub class object.
        """
        screenlockers: dict = {
           'cinnamon': [LightLocker, CinnamonLocker, GnomeLocker, Xlock],
           'gnome': [LightLocker, GnomeLocker, Xlock],
           'kde': [LightLocker, KdeLocker, Xlock],
           'macos': [MacLocker],
           'mate': [LightLocker, MateLocker, Xlock],
           'xfce': [LightLocker, GnomeLocker, XfceLocker, Xlock],
        }
        default = [LightLocker, Xlock]

        for screenlocker in screenlockers.get(desktop, default):
            locker = screenlocker()
            if locker.detect():
                return locker

        raise SystemExit(f"{sys.argv[0]}: Cannot find suitable screen locker.")

    def run(self) -> None:
        """
        Run screen locker.
        """
        if self._daemon:
            tasks = Tasks.factory()
            cmdline = self._daemon.get_cmdline()
            if not tasks.haspname(Path(cmdline[0]).name):
                Background(cmdline).run()
                time.sleep(1)

        Background(self._command.get_cmdline()).run()


class CinnamonLocker(ScreenLocker):
    """
    Cinnamon screen locker class.
    """

    def _setup(self) -> None:
        self._daemon = Command('cinnamon-screensaver', errors='ignore')
        self._command = Command(
            'cinnamon-screensaver-command',
            args=['--lock'],
            errors='ignore',
        )


class GnomeLocker(ScreenLocker):
    """
    Gnome screen locker class.
    """

    def _setup(self) -> None:
        self._daemon = Command('gnome-screensaver', errors='ignore')
        self._command = Command(
            'gnome-screensaver-command',
            args=['--lock'],
            errors='ignore',
        )


class KdeLocker(ScreenLocker):
    """
    KDE screen locker class.
    """

    def _setup(self) -> None:
        self._command = Command(
            'qdbus',
            args=['org.freedesktop.ScreenSaver', '/ScreenSaver', 'Lock'],
            errors='ignore',
        )


class LightLocker(ScreenLocker):
    """
    Light DM screen locker class.
    """

    def _setup(self) -> None:
        self._daemon = Command('light-locker', errors='ignore')
        self._command = Command(
            'light-locker-command',
            args=['--lock'],
            errors='ignore',
        )


class MacLocker(ScreenLocker):
    """
    Mac screen locker class.
    """

    def _setup(self) -> None:
        self._command = Command(
            'pmset',
            args=['displaysleepnow'],
            errors='ignore',
        )


class MateLocker(ScreenLocker):
    """
    Mate screen locker class.
    """

    def _setup(self) -> None:
        self._daemon = Command('mate-screensaver', errors='ignore')
        self._command = Command(
            'mate-screensaver-command',
            args=['--lock'],
            errors='ignore',
        )


class XfceLocker(ScreenLocker):
    """
    XFCE screen locker class.
    """

    def _setup(self) -> None:
        self._command = Command('xflock4', errors='ignore')


class Xlock(ScreenLocker):
    """
    "xlock" screen locker class.
    """

    def _setup(self) -> None:
        self._command = Command('xlock', errors='ignore')
        args = sys.argv[1:]
        if args:
            self._command.set_args(args)
        else:
            self._command.set_args([
                '-allowroot',
                '+nolock',
                '-mode',
                'blank',
                '-fg',
                'red',
                '-bg',
                'black',
                '-timeout',
                '10',
            ])


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

        if 'VNCDESKTOP' in os.environ:
            os.environ['DISPLAY'] = ':0'

    @staticmethod
    def run() -> int:
        """
        Start program
        """
        desktop = Desktop.detect()
        locker = ScreenLocker.factory(desktop)
        locker.run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
