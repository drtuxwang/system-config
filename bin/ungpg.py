#!/usr/bin/env python3
"""
Unpack an encrypted archive in gpg (pgp compatible) format.
"""

import argparse
import glob
import os
import signal
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
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_files(self) -> List[str]:
        """
        Return list of files.
        """
        return self._args.files

    def get_gpg(self) -> command_mod.Command:
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
    def _set_libraries(command: command_mod.Command) -> None:
        libdir = Path(Path(command.get_file()).parent, 'lib')
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

        self._gpg = command_mod.Command('gpg2', errors='ignore')
        if not self._gpg.is_found():
            self._gpg = command_mod.Command('gpg', errors='stop')

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
        view_flag = options.get_view_flag()
        gpg = options.get_gpg()

        task: subtask_mod.Task
        for path in [Path(x) for x in options.get_files()]:
            if not path.is_file():
                raise SystemExit(f'{sys.argv[0]}: Cannot find "{path}" file.')

            if view_flag:
                task = subtask_mod.Batch(
                    gpg.get_cmdline() + ['--list-packets', path]
                )
                task.run(env={'GPG_TTY': None})
                print(f"\n{path}:")
                for line in task.get_output():
                    print(line)
                continue

            task = subtask_mod.Task(gpg.get_cmdline() + [path])
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )

            path_new = Path(path.parent, path.stem)
            if path_new.is_file():
                file_time = int(path.stat().st_mtime)
                os.utime(path_new, (file_time, file_time))

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
