#!/usr/bin/env python3
"""
Wrapper for "git" command
"""

import getpass
import os
import signal
import socket
import sys
from pathlib import Path
from typing import List

import command_mod
import subtask_mod


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self.parse(sys.argv)

    def get_env(self) -> dict:
        """
        Return dictionary of environments.
        """
        return self._env

    def get_git(self) -> command_mod.Command:
        """
        Return git Command class object.
        """
        return self._git

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
        self._git = command_mod.Command(Path('bin', 'git'), errors='stop')
        self._git.set_args(args[1:])

        self._env = {}
        if not Path(f'{self._git.get_cmdline()[0]}.py').is_file():
            git_home = Path(self._git.get_file()).parents[1]
            if git_home not in ('/usr', '/usr/local', '/opt/software'):
                self._env['GIT_EXEC_PATH'] = str(
                    Path(git_home, 'libexec', 'git-core')
                )
                self._env['GIT_TEMPLATE_DIR'] = str(
                    Path(git_home, 'share', 'git-core', 'templates')
                )
        os.umask(0o022)

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

        subtask_mod.Exec(
            options.get_git().get_cmdline()).run(env=options.get_env())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
