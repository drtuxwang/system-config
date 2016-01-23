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

import syslib

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

    def get_copy_link_flag(self):
        """
        Return copy link flag.
        """
        return self._args.copyLinkFlag

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
        parser = argparse.ArgumentParser(description='Copy files and directories.')

        parser.add_argument('-f', dest='copyLinkFlag', action='store_true',
                            help='Follow links and copy file/directory.')

        parser.add_argument('sources', nargs='+', metavar='source',
                            help='Source file or directory.')
        parser.add_argument('target', nargs=1, metavar='target',
                            help='Target file or directory.')

        self._args = parser.parse_args(args)


class Copy(object):
    """
    Copy class
    """

    def __init__(self, options):
        self._options = options
        self._automount(options.get_target(), 8)
        if len(options.get_sources()) > 1:
            if not os.path.isdir(options.get_target()):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + options.get_target() + '" target directory.')
        for source in options.get_sources():
            if os.path.isdir(source):
                if os.path.isabs(source) or source.split(os.sep)[0] in (os.curdir, os.pardir):
                    targetdir = options.get_target()
                    self._copy(source, os.path.join(options.get_target(), os.path.basename(source)))
                else:
                    targetdir = os.path.dirname(os.path.join(options.get_target(), source))
                    if not os.path.isdir(targetdir):
                        try:
                            os.makedirs(targetdir)
                            os.chmod(targetdir, syslib.FileStat(source).get_mode())
                        except OSError:
                            raise SystemExit(
                                sys.argv[0] + ': Cannot create "' + targetdir + '" directory.')
                    self._copy(source, os.path.join(options.get_target(), source))
            else:
                directory = os.path.join(options.get_target(), os.path.dirname(source))
                if not os.path.isdir(directory):
                    try:
                        os.makedirs(directory)
                    except OSError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create "' + directory + '" directory.')
                self._copy(source, os.path.join(options.get_target(), source))

    def _automount(self, directory, wait):
        if directory.startswith('/media/'):
            for _ in range(0, wait * 10):
                if os.path.isdir(directory):
                    break
                time.sleep(0.1)

    def _copy(self, source, target):
        if self._options.get_copy_link_flag() and os.path.islink(source):
            print('Copying "' + source + '" link...')
            source_link = os.readlink(source)
            if os.path.islink(target) or os.path.isfile(target):
                try:
                    os.remove(target)
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot remove "' + target + '" link.')
            try:
                os.symlink(source_link, target)
            except OSError:
                raise SystemExit(sys.argv[0] + ': Cannot create "' + target + '" link.')
        elif os.path.isdir(source):
            print('Copying "' + source + '" directory...')
            try:
                files = sorted([os.path.join(source, x) for x in os.listdir(source)])
            except PermissionError:
                raise SystemExit(sys.argv[0] + ': Cannot open "' + source + '" directory.')
            if not os.path.isdir(target):
                try:
                    os.makedirs(target)
                    os.chmod(target, syslib.FileStat(source).get_mode())
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + target + '" directory.')
            for file in files:
                self._copy(file, os.path.join(target, os.path.basename(file)))
        elif os.path.isfile(source):
            print('Copying "' + source + '" file...')
            try:
                shutil.copy2(source, target)
            except OSError as exception:
                if exception.args != (95, 'Operation not supported'):  # os.listxattr for ACL
                    try:
                        with open(source, 'rb'):
                            raise SystemExit(sys.argv[0] + ': Cannot create "' + target + '" file.')
                    except OSError:
                        raise SystemExit(sys.argv[0] + ': Cannot create "' + target + '" file.')
            except shutil.Error as exception:
                if 'are the same file' in exception.args[0]:
                    raise SystemExit(sys.argv[0] + ': Cannot copy to same "' + target + '" file.')
                else:
                    raise SystemExit(sys.argv[0] + ': Cannot copy to "' + target + '" file.')


class Main(object):
    """
    Main class
    """

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windows_argv()
        try:
            options = Options(sys.argv)
            Copy(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except (syslib.SyslibError, SystemExit) as exception:
            sys.exit(exception)
        sys.exit(0)

    def _signals(self):
        if hasattr(signal, 'SIGPIPE'):
            signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    def _windows_argv(self):
        argv = []
        for arg in sys.argv:
            files = glob.glob(arg)  # Fixes Windows globbing bug
            if files:
                argv.extend(files)
            else:
                argv.append(arg)
        sys.argv = argv


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
