#!/usr/bin/env python3
"""
Wrapper for "git" command
"""

import getpass
import glob
import os
import signal
import socket
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from subtask_mod import Exec


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

    def get_git(self) -> Command:
        """
        Return git Command class object.
        """
        return self._git

    @staticmethod
    def _config() -> None:
        path = Path(Path.home(), '.gitconfig')
        if not path.is_file():
            try:
                with path.open('w', newline='\n') as ofile:
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
        self._git = Command('bin/git', errors='stop')
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
        if os.name == 'nt':
            argv = []
            for arg in sys.argv:
                files = sorted(glob.glob(arg))  # Fixes Windows globbing bug
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

        Exec(options.get_git().get_cmdline()).run(env=options.get_env())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
