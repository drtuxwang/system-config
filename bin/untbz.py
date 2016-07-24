#!/usr/bin/env python3
"""
Unpack a compressed archive in TAR.BZ2 format.
"""

import argparse
import glob
import os
import signal
import sys
import tarfile

if sys.version_info < (3, 3) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.3, < 4.0).')


class Options(object):
    """
    Options class
    """

    def __init__(self):
        self._args = None
        self.parse(sys.argv)

    def get_archives(self):
        """
        Return list of archives.
        """
        return self._args.archives

    def get_view_flag(self):
        """
        Return view flag.
        """
        return self._args.view_flag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(
            description='Unpack a compressed archive in TAR.BZ2 format.')

        parser.add_argument(
            '-v',
            dest='view_flag',
            action='store_true',
            help='Show contents of archive.'
        )
        parser.add_argument(
            'archives',
            nargs='+',
            metavar='file.tar.bz2|file.tbz',
            help='Archive file.'
        )

        self._args = parser.parse_args(args)

        for archive in self._args.archives:
            if (not archive.endswith('.tar.bz2') and not
                    archive.endswith('.tbz')):
                raise SystemExit(
                    sys.argv[0] + ': Unsupported "' + archive +
                    '" archive format.'
                )

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

    def _unpack(self):
        for file in self._archive.getnames():
            print(file)
            if os.path.isabs(file):
                raise SystemExit(
                    sys.argv[0] + ': Unsafe to extract file with absolute '
                    'path outside of current directory.'
                )
            elif file.startswith(os.pardir):
                raise SystemExit(
                    sys.argv[0] + ': Unsafe to extract file with relative '
                    'path outside of current directory.'
                )
            try:
                self._archive.extract(self._archive.getmember(file))
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Unable to create "' + file +
                    '" extracted.'
                )
            if not os.path.isfile(file):
                if not os.path.isdir(file):
                    if not os.path.islink(file):
                        raise SystemExit(
                            sys.argv[0] + ': Cannot create extracted "' +
                            file + '" file.'
                        )

    def _view(self):
        self._archive.list()

    def run(self):
        """
        Start program
        """
        options = Options()

        os.umask(int('022', 8))
        for archive in options.get_archives():
            print(archive + ':')
            try:
                self._archive = tarfile.open(archive, 'r:bz2')
            except OSError:
                raise SystemExit(
                    sys.argv[0] + ': Cannot open "' + archive +
                    '" archive file.'
                )
            if options.get_view_flag():
                self._view()
            else:
                self._unpack()


if __name__ == '__main__':
    if '--pydoc' in sys.argv:
        help(__name__)
    else:
        Main()
