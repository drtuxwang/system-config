#!/usr/bin/env python3
"""
Modify file time to original GIT author time.
"""

import argparse
import glob
import os
import signal
import sys
from typing import List

import git  # type: ignore


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

    def get_recursive_flag(self) -> bool:
        """
        Return recursive flag.
        """
        return self._args.recursive_flag

    def _parse_args(self, args: List[str]) -> None:
        parser = argparse.ArgumentParser(
            description="Modify file time to original GIT author time.",
        )

        parser.add_argument(
            '-r',
            dest='recursive_flag',
            action='store_true',
            help="Recursive into sub-directories.",
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help="File in a GIT repository.",
        )

        self._args = parser.parse_args(args)

    def parse(self, args: List[str]) -> None:
        """
        Parse arguments
        """
        self._parse_args(args[1:])


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
                files = glob.glob(arg)  # Fixes Windows globbing bug
                if files:
                    argv.extend(files)
                else:
                    argv.append(arg)
            sys.argv = argv

    @classmethod
    def _update(
        cls,
        repo: git.Repo,
        files: List[str],
        recursive: bool,
    ) -> None:
        for file in files:
            if os.path.isfile(file):
                try:
                    commit = next(repo.iter_commits(
                        paths=os.path.abspath(file),
                        max_count=1,
                    ))
                except StopIteration:  # Non git file
                    pass
                else:
                    author_time = commit.committed_date
                    try:
                        os.utime(file, (author_time, author_time))
                    except (IndexError, ValueError):
                        pass
            elif recursive and os.path.isdir(file):
                cls._update(
                    repo,
                    glob.glob(os.path.join(file, '*')),
                    recursive,
                )

    def run(self) -> int:
        """
        Start program
        """
        options = Options()

        try:
            repo = git.Repo('./', search_parent_directories=True)
        except (
            git.InvalidGitRepositoryError  # pylint: disable=no-member
        ) as exception:
            raise SystemExit(
                f'{sys.argv[0]}: Cannot find .git directory.',
            ) from exception
        self._update(repo, options.get_files(), options.get_recursive_flag())

        return 0


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
