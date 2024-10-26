#!/usr/bin/env python3
"""
Wrapper for "vncserver" command
"""

import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from subtask_mod import Exec, Task


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_vncserver(self) -> Command:
        """
        Return vncserver Command class object.
        """
        return self._vncserver

    def _config(self) -> None:
        directory_path = Path(Path.home(), '.vnc')
        if not directory_path.is_dir():
            directory_path.mkdir(mode=0o700)

        if len(sys.argv) == 1 and not Path(directory_path, 'passwd').is_file():
            raise SystemExit(
                f'{sys.argv[0]}: ".vnc/passwd" does not exist. '
                'Run "vncpasswd" or use "-SecurityTypes=None".',
            )
        os.chdir(Path.home())
        path = Path(directory_path, 'xstartup')
        if not path.is_file():
            answer = input(
                "Would you like to use GNOME(g), KDE(k) or XFCE(x)? "
            )
            try:
                with path.open('w') as ofile:
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
                    f'{sys.argv[0]}: Cannot create ".vnc/xstartup" file.',
                ) from exception
            path.chmod(0o755 & ~self._umask)
        directory_path = Path(self._vncserver.get_file()).parent
        if (
            'PATH' in os.environ and
            str(directory_path) not in os.environ['PATH'].split(os.pathsep)
        ):
            os.environ['PATH'] = (
                f"{directory_path}{os.pathsep}{os.environ['PATH']}"
            )

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._vncserver = Command(
            'tigervncserver',
            pathextra=['/usr/bin'],
            errors='stop'
        )
        if sys.argv[-1] in ('-help', '-version'):
            Exec(self._vncserver.get_cmdline() + sys.argv[1:]).run()
        self._vncserver.set_args([
            '-geometry',
            '1280x720',
            '-depth',
            '24',
            '-localhost',
            '-SecurityTypes',
            'X509Vnc,TLSVnc',
        ] + args[1:])
        self._umask = os.umask(0o077)
        os.umask(self._umask)
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

        pattern = 'Cannot write random bytes:|RAND_write_file'
        task = Task(options.get_vncserver().get_cmdline())
        task.run(directory=os.getenv('HOME', '/'), pattern=pattern)

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
