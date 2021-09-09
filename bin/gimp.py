#!/usr/bin/env python3
"""
Sandbox for "gimp" launcher
"""

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
    def run() -> int:
        """
        Start program
        """
        gimp = network_mod.Sandbox('gimp', errors='stop')
        gimp.set_args(['--no-splash'] + sys.argv[1:])
        if os.path.isfile(gimp.get_file() + '.py'):
            subtask_mod.Exec(gimp.get_cmdline()).run()

        desktopintegration = os.path.join(
            os.getenv('HOME', '/'),
            '.local/share/appimagekit',
            'GNUImageManipulationProgram_no_desktopintegration',
        )
        if not os.path.isfile(desktopintegration):
            if not os.path.isdir(os.path.dirname(desktopintegration)):
                os.makedirs(os.path.dirname(desktopintegration))
            with open(desktopintegration, 'wb'):
                pass
        configs = [
            desktopintegration + ':ro',
            '/run/user/{0:d}'.format(os.getuid()),
        ]
        work_dir = os.environ['PWD']  # "os.getcwd()" returns realpath instead
        if work_dir == os.environ['HOME']:
            desktop = os.path.join(work_dir, 'Desktop')
            if os.path.isdir(desktop):
                os.chdir(desktop)
                work_dir = desktop
        configs.extend([
            os.path.join(os.getenv('HOME', '/'), '.config/GIMP-AppImage'),
            work_dir,
        ])
        if len(sys.argv) >= 2:
            if os.path.isdir(sys.argv[1]):
                configs.append(os.path.abspath(sys.argv[1]))
            elif os.path.isfile(sys.argv[1]):
                configs.append(os.path.dirname(os.path.abspath(sys.argv[1])))
            if sys.argv[1] == '-net':
                gimp.set_args(['--no-splash'] + sys.argv[2:])
        gimp.sandbox(configs)

        subtask_mod.Daemon(gimp.get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
