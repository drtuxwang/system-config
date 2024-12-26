#!/usr/bin/env python3
"""
Unpack an encrypted archive in gpg (pgp compatible) format.
"""

import argparse
import os
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from subtask_mod import Batch, Task


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def get_gpg(self) -> Command:
        """
        Return gpg Command class object.
        """
        return self._gpg

    def get_view_flag(self) -> bool:
        """
        Return view flag.
        """
        return self._args.view_flag

    @staticmethod
    def _config() -> None:
        os.umask(0o077)
        gpgdir = Path(Path.home(), '.gnupg')
        if not gpgdir.is_dir():
            try:
                gpgdir.mkdir()
            except OSError:
                return
        if 'DISPLAY' in os.environ:
            del os.environ['DISPLAY']

    @staticmethod
    def _set_libraries(command: Command) -> None:
        libdir = Path(command.get_file()).with_name('lib')
        if libdir.is_dir() and os.name == 'posix':
            if os.uname()[0] == 'Linux':
                if 'LD_LIBRARY_PATH' in os.environ:
                    os.environ['LD_LIBRARY_PATH'] = (
                        f"{libdir}{os.pathsep}{os.environ['LD_LIBRARY_PATH']}"
                    )
                else:
                    os.environ['LD_LIBRARY_PATH'] = str(libdir)

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Unpack an encrypted archive in gpg "
            "(pgp compatible) format.",
        )

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help="Show contents of archive.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file.gpg|file.pgp',
            help="GPG/PGP encrypted file.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._gpg = Command('gpg2', errors='ignore')
        if not self._gpg.is_found():
            self._gpg = Command('gpg', errors='stop')

        self._config()
        self._set_libraries(self._gpg)


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
        view_flag = options.get_view_flag()
        gpg = options.get_gpg()

        task: Task
        for path in [Path(x) for x in options.get_files()]:
            if not path.is_file():
                raise SystemExit(f'{sys.argv[0]}: Cannot find "{path}" file.')

            if view_flag:
                task = Batch(gpg.get_cmdline() + ['--list-packets', path])
                task.run(env={'GPG_TTY': None})
                print(f"\n{path}:")
                for line in task.get_output():
                    print(line)
                continue

            task = Task(gpg.get_cmdline() + [path])
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )

            path_new = path.with_name(path.stem)
            if path_new.is_file():
                file_time = int(path.stat().st_mtime)
                os.utime(path_new, (file_time, file_time))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
