#!/usr/bin/env python3
"""
Wrapper for GNOME/KDE/XFCE screen lock
"""

import glob
import os
import signal
import sys
import time

import desktop_mod
import command_mod
import subtask_mod
import task_mod

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Main(object):
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
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
    def run():
        """
        Start program
        """
        desktop = desktop_mod.Desktop.detect()
        tasks = task_mod.Tasks.factory()

        xlock = command_mod.Command(
            'light-locker-command',
            args=['--lock'],
            errors='ignore'
        )
        if xlock.is_found():
            tasks.killpname('gnome-screensaver')
            if not task_mod.Tasks.factory().haspname('light-locker'):
                command = command_mod.Command('light-locker', errors='stop')
                subtask_mod.Daemon(command.get_cmdline()).run()
                time.sleep(1)
        elif desktop == 'gnome':
            xlock = command_mod.Command(
                'gnome-screensaver-command',
                args=['--lock'],
                errors='stop'
            )
            if not tasks.haspname('gnome-screensaver'):
                command = command_mod.Command(
                    'gnome-screensaver',
                    errors='stop'
                )
                subtask_mod.Task(command.get_cmdline()).run()
        elif desktop == 'kde':
            xlock = command_mod.Command(
                'qdbus',
                args=['org.freedesktop.ScreenSaver', '/ScreenSaver', 'Lock'],
                errors='stop'
            )
        elif desktop == 'xfce':
            xlock = command_mod.Command('xflock4', errors='stop')
        elif desktop == 'macos':

            xlock = command_mod.Command(
                '/System/Library/CoreServices/Menu Extras/User.menu/'
                'Contents/Resources/CGSession',
                args=['-suspend'],
                errors='stop'
            )
        else:
            xlock = command_mod.Command('xlock', args=[
                '-allowroot',
                '+nolock',
                '-mode',
                'blank',
                '-fg',
                'red',
                '-bg',
                'black',
                '-timeout',
                '10'
            ], errors='stop')
        if 'VNCDESKTOP' in os.environ:
            os.environ['DISPLAY'] = ':0'
        subtask_mod.Background(xlock.get_cmdline() + sys.argv[1:]).run()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
