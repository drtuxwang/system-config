#!/usr/bin/env python3
"""
Recursively link all files.
"""

import argparse
import glob
import os
import signal
import sys


class Options:
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_directories(self):
        """
        Return list of directories.
        """
        return self._args.directories

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Recursively link all files.')

        parser.add_argument(
            'directories',
            nargs='+',
            metavar='directory',
            help='Directory containing files to link.'
        )

        self._args = parser.parse_args(args)

        for directory in self._args.directories:
            if not os.path.isdir(directory):
                raise SystemExit(
                    sys.argv[0] + ': Source directory "' + directory +
                    '" does not exist.'
                )
            if os.path.samefile(directory, os.getcwd()):
                raise SystemExit(
                    sys.argv[0] + ': Source directory "' + directory +
                    '" cannot be current directory.'
                )

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

    def _link_files(self, source_dir, target_dir, subdir=''):
        try:
            source_files = sorted([
                os.path.join(source_dir, x)
                for x in os.listdir(source_dir)
            ])
        except PermissionError:
            return
        if not os.path.isdir(target_dir):
            print('Creating "' + target_dir + '" directory...')
            try:
                os.mkdir(target_dir)
            except OSError as exception:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + target_dir +
                    '" directory.'
                ) from exception

        for source_file in sorted(source_files):
            target_file = os.path.join(
                target_dir,
                os.path.basename(source_file)
            )
            if os.path.isdir(source_file):
                self._link_files(
                    source_file,
                    target_file,
                    os.path.join(os.pardir, subdir)
                )
            else:
                if os.path.islink(target_file):
                    print('Updating "' + target_file + '" link...')
                    try:
                        os.remove(target_file)
                    except OSError as exception:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot remove "' + target_file +
                            '" link.'
                        ) from exception
                else:
                    print('Creating "' + target_file + '" link...')
                try:
                    if os.path.isabs(source_file):
                        os.symlink(source_file, target_file)
                    else:
                        os.symlink(
                            os.path.join(subdir, source_file),
                            target_file
                        )
                except OSError as exception:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot create "' +
                        target_file + '" link.'
                    ) from exception

    def run(self):
        """
        Start program
        """
        options = Options()

        for directory in options.get_directories():
            self._link_files(directory, '.')


if '--pydoc' in sys.argv:
    help(__name__)
else:
    Main()
