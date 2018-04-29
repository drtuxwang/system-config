#!/usr/bin/env python3
"""
Copy files and directories.
"""

import argparse
import glob
import os
import shutil
import signal
import sys
import time

import file_mod

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ": Requires Python version (>= 3.3, < 4.0).")


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_sources(self):
        """
        Return list of source files.
        """
        return self._args.sources

    def get_target(self):
        """
        Return target file or directory.
        """
        return self._args.target[0]

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Copy files and directories.')

        parser.add_argument(
            'sources',
            nargs='+',
            metavar='source',
            help='Source file or directory.'
        )
        parser.add_argument(
            'target',
            nargs=1,
            metavar='target',
            help='Target file or directory.'
        )

        self._args = parser.parse_args(args)

    def parse(self, args):
        """
        Parse arguments
        """
        self._parse_args(args[1:])


class Main(object):
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
    def _automount(directory, wait):
        if directory.startswith('/media/'):
            for _ in range(0, wait * 10):
                if os.path.isdir(directory):
                    break
                time.sleep(0.1)

    @staticmethod
    def _copy_link(source, target):
        print('Copying "' + source + '" link...')
        source_link = os.readlink(source)

        if os.path.isfile(target):
            try:
                os.remove(target)
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot remove "' + target + '" link.')
        try:
            os.symlink(source_link, target)
        except OSError:
            raise SystemExit(
                sys.argv[0] + ': Cannot create "' + target + '" link.')

    def _copy_directory(self, source, target):
        print('Copying "' + source + '" directory...')
        try:
            files = sorted(
                [os.path.join(source, x) for x in os.listdir(source)])
        except PermissionError:
            raise SystemExit(
                sys.argv[0] + ': Cannot open "' + source + '" directory.')
        if not os.path.isdir(target):
            try:
                os.makedirs(target)
                os.chmod(target, file_mod.FileStat(source).get_mode())
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot create "' + target +
                    '" directory.'
                )
        for file in files:
            self._copy(file, os.path.join(target, os.path.basename(file)))

    @staticmethod
    def _copy_file(source, target):
        print('Copying "' + source + '" file...')
        try:
            shutil.copy2(source, target)
        except shutil.Error as exception:
            if 'are the same file' in exception.args[0]:
                raise SystemExit(
                    sys.argv[0] + ': Cannot copy to same "' +
                    target + '" file.'
                )
            else:
                raise SystemExit(
                    sys.argv[0] + ': Cannot copy to "' + target + '" file.')
        except OSError as exception:
            if exception.args != (95, 'Operation not supported'):
                try:
                    with open(source, 'rb'):
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create "' +
                            target + '" file.'
                        )
                except OSError:
                    raise SystemExit(
                        sys.argv[0] + ': Cannot create "' + target + '" file.')

    def _copy(self, source, target):
        if os.path.islink(source):
            self._copy_link(source, target)
        elif os.path.isdir(source):
            self._copy_directory(source, target)
        elif os.path.isfile(source):
            self._copy_file(source, target)

    def run(self):
        """
        Start program
        """
        self._options = Options()
        target = self._options.get_target()

        self._automount(target, 8)
        if len(self._options.get_sources()) > 1:
            if not os.path.isdir(target):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + target +
                    '" target directory.'
                )
        for source in self._options.get_sources():
            if os.path.isdir(source):
                if (os.path.isabs(source) or
                        source.split(os.sep)[0] in (os.curdir, os.pardir)):
                    targetdir = target
                    self._copy(
                        source,
                        os.path.join(target, os.path.basename(source))
                    )
                else:
                    targetdir = os.path.dirname(os.path.join(target, source))
                    if not os.path.isdir(targetdir):
                        try:
                            os.makedirs(targetdir)
                            os.chmod(
                                targetdir,
                                file_mod.FileStat(source).get_mode()
                            )
                        except OSError:
                            raise SystemExit(
                                sys.argv[0] + ': Cannot create "' +
                                targetdir + '" directory.'
                            )
                    self._copy(source, os.path.join(target, source))
            else:
                directory = os.path.join(target, os.path.dirname(source))
                if not os.path.isdir(directory):
                    try:
                        os.makedirs(directory)
                    except OSError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create "' + directory +
                            '" directory.'
                        )
                self._copy(source, os.path.join(target, source))


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
