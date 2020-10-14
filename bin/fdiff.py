#!/usr/bin/env python3
"""
Show summary of differences between two directories recursively.
"""

import argparse
import glob
import os
import signal
import sys

import file_mod


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Show summary of differences between two '
            'directories recursively.'
        )

        parser.add_argument(
            'directories',
            nargs=2,
            metavar='directory',
            help='Directory to compare.'
        )

        self._args = parser.parse_args(args)

    def get_directory_1(self):
        """
        Return directory 1.
        """
        return self._args.directories[0]

    def get_directory_2(self):
        """
        Return directory 2.
        """
        return self._args.directories[1]

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

    @staticmethod
    def _get_files(directory):
        try:
            files = sorted(
                [os.path.join(directory, x) for x in os.listdir(directory)])
        except (
            FileNotFoundError,
            NotADirectoryError,
            PermissionError,
        ) as exception:
            raise SystemExit(
                sys.argv[0] + ': Cannot open "' + directory + '" directory.'
            ) from exception
        return files

    def _diffdir(self, directory1, directory2):
        files1 = self._get_files(directory1)
        files2 = self._get_files(directory2)

        for file in files1:
            if os.path.isdir(file):
                if os.path.isdir(
                        os.path.join(directory2, os.path.basename(file))):
                    self._diffdir(
                        file,
                        os.path.join(directory2, os.path.basename(file))
                    )
                else:
                    print("only ", file + os.sep)
            elif os.path.isfile(file):
                if os.path.isfile(
                        os.path.join(directory2, os.path.basename(file))):
                    self._difffile(
                        file,
                        os.path.join(directory2, os.path.basename(file))
                    )
                else:
                    print("only ", file)

        for file in files2:
            if os.path.isdir(file):
                if not os.path.isdir(
                        os.path.join(directory1, os.path.basename(file))):
                    print("only ", file + os.sep)
            elif os.path.isfile(file):
                if not os.path.isfile(
                        os.path.join(directory1, os.path.basename(file))):
                    print("only ", file)

    @staticmethod
    def _difffile(file1, file2):
        file_stat1 = file_mod.FileStat(file1)
        file_stat2 = file_mod.FileStat(file2)

        if file_stat1.get_size() != file_stat2.get_size():
            print("diff ", file1 + "  " + file2)
        elif file_stat1.get_time() != file_stat2.get_time():
            try:
                ifile1 = open(file1, 'rb')
            except OSError:
                print("diff ", file1 + '  ' + file2)
                return
            try:
                ifile2 = open(file2, 'rb')
            except OSError:
                print("diff ", file1 + '  ' + file2)
                return
            for _ in range(0, file_stat1.get_size(), 131072):
                chunk1 = ifile1.read(131072)
                chunk2 = ifile2.read(131072)
                if chunk1 != chunk2:
                    print("diff ", file1 + '  ' + file2)
                    return
            ifile1.close()
            ifile2.close()

    def run(self):
        """
        Start program
        """
        options = Options()

        self._diffdir(options.get_directory_1(), options.get_directory_2())


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
