#!/usr/bin/env python3
"""
Unpack an archive in TAR format.
"""

import argparse
import glob
import os
import signal
import sys
import tarfile

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')


class Options:

    def __init__(self, args):
        self._parseArgs(args[1:])

    def getArchives(self):
        """
        Return list of archives.
        """
        return self._args.archives

    def getViewFlag(self):
        """
        Return view flag.
        """
        return self._args.viewFlag

    def _parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Unpack an archive in TAR format.')

        parser.add_argument('-v', dest='viewFlag', action='store_true',
                            help='Show contents of archive.')

        parser.add_argument('archives', nargs='+', metavar='file.tar', help='Archive file.')

        self._args = parser.parse_args(args)

        for archive in self._args.archives:
            if not archive.endswith('.tar'):
                raise SystemExit(sys.argv[0] + ': Unsupported "' + archive + '" archive format.')


class Unpack:

    def __init__(self, options):
        os.umask(int('022', 8))
        for archive in options.getArchives():
            if archive.endswith('.tar'):
                print(archive + ':')
                try:
                    self._archive = tarfile.open(archive, 'r:')
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot open "' + archive + '" archive file.')
                if options.getViewFlag():
                    self._view()
                else:
                    self._unpack()

    def _unpack(self):
        for file in self._archive.getnames():
            print(file)
            if os.path.isabs(file):
                raise SystemExit(sys.argv[0] + ': Unsafe to extract file with absolute path '
                                               'outside of current directory.')
            elif file.startswith(os.pardir):
                raise SystemExit(sys.argv[0] + ': Unsafe to extract file with relative path '
                                               'outside of current directory.')
            try:
                self._archive.extract(self._archive.getmember(file))
            except (IOError, OSError):
                raise SystemExit(sys.argv[0] + ': Unable to create "' + file + '" extracted.')
            if not os.path.isfile(file):
                if not os.path.isdir(file):
                    if not os.path.islink(file):
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create extracted "' + file + '" file.')

    def _view(self):
        self._archive.list()


class Main:

    def __init__(self):
        self._signals()
        if os.name == 'nt':
            self._windowsArgv()
        try:
            options = Options(sys.argv)
            Unpack(options)
        except (EOFError, KeyboardInterrupt):
            sys.exit(114)
        except SystemExit as exception:
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
