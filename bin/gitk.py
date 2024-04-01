#!/usr/bin/env python3
"""
Wrapper for "gitk" commamd
"""

import getpass
import os
import signal
import socket
import sys
from pathlib import Path
from typing import Dict, List

from command_mod import Command
from subtask_mod import Exec


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_env(self) -> Dict[str, str]:
        """
        Return dictionary of environments.
        """
        return self._env

    def get_gitk(self) -> Command:
        """
        Return gitk Command class object.
        """
        return self._gitk

    @staticmethod
    def _config() -> None:
        path = Path(Path.home(), '.gitconfig')
        if not path.is_file():
            try:
                with path.open('w') as ofile:
                    user = getpass.getuser()
                    host = socket.gethostname().split('.')[0].lower()
                    print("[user]", file=ofile)
                    print(f"        name = {user}", file=ofile)
                    print(f"        email = {user}@{host}", file=ofile)
            except OSError:
                pass

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._gitk = Command(Path('bin', 'gitk'), errors='stop')
        self._gitk.set_args(args[1:])

        self._env = {}
        if os.name == 'nt':
            os.environ['PATH'] = str(
                Path(os.environ['PATH'], Path(self._gitk.get_file()).parent)
            )
        elif not Path(f'{self._gitk.get_cmdline()[0]}.py').is_file():
            git_home = Path(self._gitk.get_file()).parents[1]
            if str(git_home) not in ('/usr', '/usr/local', '/opt/software'):
                self._env['GIT_EXEC_PATH'] = str(
                    Path(git_home, 'libexec', 'git-core')
                )
                self._env['GIT_TEMPLATE_DIR'] = str(
                    Path(git_home, 'share', 'git-core', 'templates')
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

        Exec(options.get_gitk().get_cmdline()).run(env=options.get_env())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
