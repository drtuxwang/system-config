#!/usr/bin/env python3
"""
Multi-threaded download accelerator.
"""

import argparse
import os
import shutil
import signal
import sys
from pathlib import Path
from typing import List

from command_mod import Command
from subtask_mod import Task


class Options:
    """
    Options class
    """

    def __init__(self) -> None:
        self._args: argparse.Namespace = None
        self.parse(sys.argv)

    def get_threads(self) -> int:
        """
        Return number of threads.
        """
        return self._args.threads[0]

    def get_urls(self) -> List[str]:
        """
        Return list of urls.
        """
        return self._args.urls

    def get_aria2c(self) -> Command:
        """
        Return aria2c Command class object.
        """
        return self._aria2c

    @staticmethod
    def _set_libraries(command: Command) -> None:
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
            description="Multi-threaded download accelerator.",
        )

        parser.add_argument(
            '-threads',
            nargs=1,
            type=int,
            default=[4],
            help="Number of threads. Default is 4.",
        )
        parser.add_argument(
            'urls',
            nargs='+',
            metavar='url|file.url',
            help="URL or file containing URLs.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])

        self._aria2c = Command('aria2c', errors='stop')
        self._set_libraries(self._aria2c)

        if self._args.threads[0] < 1:
            raise SystemExit(
                f'{sys.argv[0]}: You must specific a positive integer for '
                'number of threads.',
            )


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
    def _get_local(directory: str, files_local: List[str]) -> None:
        if files_local:
            if not Path(directory).is_dir():
                try:
                    os.mkdir(directory)
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot create '
                        f'"{directory}" directory.',
                    ) from exception
            for file in files_local:
                print(f"file://{file}")
                try:
                    shutil.copy2(file, Path(directory, Path(file).name))
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot find "{file}" file.',
                    ) from exception

    @staticmethod
    def _get_remote(aria2c: Command, files_remote: List[str]) -> None:
        if files_remote:
            cmdline = []
            for file in files_remote:
                cmdline.append(file.replace('https://', 'http://'))
            task = Task(aria2c.get_cmdline() + cmdline)
            task.run()
            if task.get_exitcode():
                raise SystemExit(
                    f'{sys.argv[0]}: Error code {task.get_exitcode()} '
                    f'received from "{task.get_file()}".',
                )

    def run(self) -> int:
        """
        Start program
        """
        self._options = Options()

        os.umask(0o022)
        aria2c = self._options.get_aria2c()

        for url in self._options.get_urls():
            files_local = []
            files_remote = [url]
            if url.endswith('.url') and Path(url).is_file():
                directory = url[:-4]
                files_remote = []
                aria2c.set_args([
                    '--file-allocation=none',
                    '--remote-time=true',
                    '--max-concurrent-downloads='
                    f'{self._options.get_threads()}',
                    f'--dir={directory}',
                    '-Z'
                ])
                try:
                    with Path(url).open(errors='replace') as ifile:
                        for line in ifile:
                            line = line.strip().split('  #')[0]
                            if line and not line.startswith('#'):
                                line = line.split(' #', 1)[0]
                                if line.startswith('file://'):
                                    if line not in files_local:
                                        files_local.append(line.replace(
                                            'file://',
                                            '',
                                            1,
                                        ))
                                elif line not in files_remote:
                                    files_remote.append(line)
                except OSError as exception:
                    raise SystemExit(
                        f'{sys.argv[0]}: Cannot read "{url}" URL file.',
                    ) from exception
                self._get_local(directory, files_local)
                self._get_remote(aria2c, files_remote)
            elif Path(url).is_dir():
                raise SystemExit(
                    f'{sys.argv[0]}: Cannot process "{url}" directory.',
                )
            else:
                aria2c.extend_args([
                    '--file-allocation=none',
                    '--remote-time=true',
                    f'--split={self._options.get_threads()}',
                ])

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
