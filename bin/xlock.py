#!/usr/bin/env python3
"""
Wrapper for Linux/Mac screen locking
"""

# Annotation: Fix Class reference run time NameError
from __future__ import annotations
import glob
import os
import signal
import sys
import time

import desktop_mod
import command_mod
import subtask_mod
import task_mod


class ScreenLocker:
    """
    Screen Locker base class.
    """

    def __init__(self) -> None:
        self._daemon: command_mod.Command = None
        self._command: command_mod.Command = None
        self._setup()

    def _setup(self) -> None:
        pass

    def detect(self) -> bool:
        """
        Return True if installed.
        """
        return self._command.is_found()

    @staticmethod
    def factory(desktop: str) -> ScreenLocker:
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

        raise SystemExit(sys.argv[0] + ': Cannot find suitable screen locker.')

    def run(self) -> None:
        """
        Run screen locker.
        """
        if self._daemon:
            tasks = task_mod.Tasks.factory()
            cmdline = self._daemon.get_cmdline()
            if not tasks.haspname(os.path.basename(cmdline[0])):
                subtask_mod.Background(cmdline).run()
                time.sleep(1)

        subtask_mod.Background(self._command.get_cmdline()).run()


class CinnamonLocker(ScreenLocker):
    """
    Cinnamon screen locker class.
    """

    def _setup(self) -> None:
        self._daemon = command_mod.Command(
            'cinnamon-screensaver',
            errors='ignore',
        )
        self._command = command_mod.Command(
            'cinnamon-screensaver-command',
            args=['--lock'],
            errors='ignore',
        )


class GnomeLocker(ScreenLocker):
    """
    Gnome screen locker class.
    """

    def _setup(self) -> None:
        self._daemon = command_mod.Command(
            'gnome-screensaver',
            errors='ignore',
        )
        self._command = command_mod.Command(
            'gnome-screensaver-command',
            args=['--lock'],
            errors='ignore',
        )


class KdeLocker(ScreenLocker):
    """
    KDE screen locker class.
    """

    def _setup(self) -> None:
        self._command = command_mod.Command(
            'qdbus',
            args=['org.freedesktop.ScreenSaver', '/ScreenSaver', 'Lock'],
            errors='ignore',
        )


class LightLocker(ScreenLocker):
    """
    Light DM screen locker class.
    """

    def _setup(self) -> None:
        self._daemon = command_mod.Command(
            'light-locker',
            errors='ignore',
        )
        self._command = command_mod.Command(
            'light-locker-command',
            args=['--lock'],
            errors='ignore',
        )


class MacLocker(ScreenLocker):
    """
    Mac screen locker class.
    """

    def _setup(self) -> None:
        self._command = command_mod.Command(
            '/System/Library/CoreServices/Menu Extras/User.menu/'
            'Contents/Resources/CGSession',
            args=['-suspend'],
            errors='ignore',
        )


class MateLocker(ScreenLocker):
    """
    Mate screen locker class.
    """

    def _setup(self) -> None:
        self._daemon = command_mod.Command(
            'mate-screensaver',
            errors='ignore',
        )
        self._command = command_mod.Command(
            'mate-screensaver-command',
            args=['--lock'],
            errors='ignore',
        )


class XfceLocker(ScreenLocker):
    """
    XFCE screen locker class.
    """

    def _setup(self) -> None:
        self._command = command_mod.Command('xflock4', errors='ignore')


class Xlock(ScreenLocker):
    """
    "xlock" screen locker class.
    """

    def _setup(self) -> None:
        self._command = command_mod.Command('xlock', errors='ignore')
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
    def run() -> int:
        """
        Start program
        """
        if 'VNCDESKTOP' in os.environ:
            os.environ['DISPLAY'] = ':0'

        desktop = desktop_mod.Desktop.detect()
        locker = ScreenLocker.factory(desktop)
        locker.run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
