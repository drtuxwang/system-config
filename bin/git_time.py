#!/usr/bin/env python3
"""
Modify file time to original GIT author time.
"""

import argparse
import glob
import os
import signal
import sys

import git

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.2, < 4.0).")


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def get_recursive_flag(self):
        """
        Return recursive flag.
        """
        return self._args.recursive_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Modify file time to original GIT author time.')

        parser.add_argument(
            '-r',
            dest='recursive_flag',
            action='store_true',
            help='Recursive into sub-directories.'
        )
        parser.add_argument(
            'files',
            nargs='+',
            metavar='file',
            help='File in a GIT repository.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Main:
    """
    Main class
    """

    def __init__(self):
        try:
            self.config()
            sys.exit(self.run())
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
            sys.exit(exception)

    @staticmethod
    def config():
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
    def _update(cls, repo, files, recursive):
        for file in files:
            if os.path.isfile(file):
                commit = next(repo.iter_commits(
                    paths=os.path.abspath(file),
                    max_count=1,
                ))
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

    def run(self):
        """
        Start program
        """
        options = Options()

        # pylint: disable = no-member
        try:
            repo = git.Repo('./', search_parent_directories=True)
        except git.exc.InvalidGitRepositoryError:
            raise SystemExit(sys.argv[0] + ': Cannot find .git directory.')
        # pylint: enable = no-member
        self._update(repo, options.get_files(), options.get_recursive_flag())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
