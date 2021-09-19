#!/usr/bin/env python3
"""
Wrapper for "vncserver" command
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

    def get_vncserver(self) -> command_mod.Command:
        """
        Return vncserver Command class object.
        """
        return self._vncserver

    def _config(self) -> None:
        if not os.path.isfile(
                os.path.join(os.environ['HOME'], '.vnc', 'passwd')):
            raise SystemExit(
                sys.argv[0] +
                ': ".vnc/passwd" does not exist. Run "vncpasswd".'
            )
        os.chdir(os.environ['HOME'])
        xstartup = os.path.join(os.environ['HOME'], '.vnc', 'xstartup')
        if not os.path.isfile(xstartup):
            answer = input(
                "Would you like to use GNOME(g), KDE(k) or XFCE(x)? "
            )
            try:
                with open(xstartup, 'w', newline='\n') as ofile:
                    print("#!/usr/bin/env bash", file=ofile)
                    print("unset DBUS_SESSION_BUS_ADDRESS", file=ofile)
                    print("unset SESSION_MANAGER", file=ofile)
                    if answer[0].lower() == 'g':
                        print("dbus-launch gnome-session", file=ofile)
                    elif answer[0].lower() == 'k':
                        print("dbus-launch startkde", file=ofile)
                    elif answer[0].lower() == 'x':
                        print("dbus-launch startxfce4", file=ofile)
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create ".vnc/xstartup" file.'
                ) from exception
            os.chmod(xstartup, int('755', 8) & ~self._umask)
        directory = os.path.dirname(self._vncserver.get_file())
        if (
            'PATH' in os.environ and
            directory not in os.environ['PATH'].split(os.pathsep)
        ):
            os.environ['PATH'] = directory + os.pathsep + os.environ['PATH']

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._vncserver = command_mod.Command(
            'tigervncserver',
            pathextra=['/usr/bin'],
            errors='stop'
        )
        self._vncserver.set_args([
            '-geometry',
            '1024x768',
            '-depth',
            '24',
            '-localhost',
            '-SecurityTypes',
            'X509Vnc,TLSVnc',
        ] + args[1:])
        self._umask = os.umask(int('077', 8))
        os.umask(self._umask)
        if len(args) == 1:
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
        options = Options()

        subtask_mod.Exec(options.get_vncserver().get_cmdline()).run()

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
