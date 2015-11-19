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

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getCopyLinkFlag(self):
        """
        Return copy link flag.
        """
        return self._args.copyLinkFlag

    def getSources(self):
        """
        Return list of source files.
        """
        return self._args.sources

    def getTarget(self):
        """
        Return target file or directory.
        """
        return self._args.target[0]

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Copy files and directories.')

        parser.add_argument('-f', dest='copyLinkFlag', action='store_true',
                            help='Follow links and copy file/directory.')

        parser.add_argument('sources', nargs='+', metavar='source',
                            help='Source file or directory.')
        parser.add_argument('target', nargs=1, metavar='target',
                            help='Target file or directory.')

        self._args = parser.parse_args(args)


class Copy:

    def __init__(self, options):
        self._options = options
        self._automount(options.getTarget(), 8)
        if len(options.getSources()) > 1:
            if not os.path.isdir(options.getTarget()):
                raise SystemExit(
                    sys.argv[0] + ': Cannot find "' + options.getTarget() + '" target directory.')
        for source in options.getSources():
            if os.path.isdir(source):
                if os.path.isabs(source) or source.split(os.sep)[0] in (os.curdir, os.pardir):
                    targetdir = options.getTarget()
                    self._copy(source, os.path.join(options.getTarget(), os.path.basename(source)))
                else:
                    targetdir = os.path.dirname(os.path.join(options.getTarget(), source))
                    if not os.path.isdir(targetdir):
                        try:
                            os.makedirs(targetdir)
                            os.chmod(targetdir, syslib.FileStat(source).getMode())
                        except OSError:
                            raise SystemExit(
                                sys.argv[0] + ': Cannot create "' + targetdir + '" directory.')
                    self._copy(source, os.path.join(options.getTarget(), source))
            else:
                directory = os.path.join(options.getTarget(), os.path.dirname(source))
                if not os.path.isdir(directory):
                    try:
                        os.makedirs(directory)
                    except OSError:
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create "' + directory + '" directory.')
                self._copy(source, os.path.join(options.getTarget(), source))

    def _automount(self, directory, wait):
        if directory.startswith('/media/'):
            for i in range(0, wait * 10):
                if os.path.isdir(directory):
                    break
                time.sleep(0.1)

    def _copy(self, source, target):
        if self._options.getCopyLinkFlag() and os.path.islink(source):
            print('Copying "' + source + '" link...')
            sourceLink = os.readlink(source)
            if os.path.islink(target) or os.path.isfile(target):
                try:
                    os.remove(target)
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot remove "' + target + '" link.')
            try:
                os.symlink(sourceLink, target)
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
                    os.chmod(target, syslib.FileStat(source).getMode())
                except OSError:
                    raise SystemExit(sys.argv[0] + ': Cannot create "' + target + '" directory.')
            for file in files:
                self._copy(file, os.path.join(target, os.path.basename(file)))
        elif os.path.isfile(source):
            print('Copying "' + source + '" file...')
            try:
                shutil.copy2(source, target)
            except IOError as exception:
                if exception.args != (95, 'Operation not supported'):  # os.listxattr for ACL
                    try:
                        with open(source, 'rb'):
                            raise SystemExit(sys.argv[0] + ': Cannot create "' + target + '" file.')
                    except IOError:
                        raise SystemExit(sys.argv[0] + ': Cannot create "' + target + '" file.')
                    except OSError:
                        raise SystemExit(sys.argv[0] + ': Cannot read "' + source + '" file.')
            except shutil.Error as exception:
                if 'are the same file' in exception.args[0]:
                    raise SystemExit(sys.argv[0] + ': Cannot copy to same "' + target + '" file.')
                else:
                    raise SystemExit(sys.argv[0] + ': Cannot copy to "' + target + '" file.')


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
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

    def _windowsArgv(self):
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
