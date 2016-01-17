#!/usr/bin/env python3
"""
Calculate MD5 checksums of files.
"""

import argparse
import glob
import hashlib
import os
import signal
import sys

import syslib

if sys.version_info < (3, 2) or sys.version_info >= (4, 0):
    sys.exit(__file__ + ': Requires Python version (>= 3.2, < 4.0).')

# pylint: disable=no-self-use,too-few-public-methods


class Options(object):
    """
    Options class
    """

    def __init__(self, args):
        self._parse_args(args[1:])

    def get_check_flag(self):
        """
        Return check flag.
        """
        return self._args.checkFlag

    def get_files(self):
        """
        Return list of files.
        """
        return self._args.files

    def get_recursive_flag(self):
        """
        Return recursive flag.
        """
        return self._args.recursiveFlag

    def _parse_args(self, args):
        parser = argparse.ArgumentParser(description='Calculate MD5 checksums of files.')

        parser.add_argument('-R', dest='recursiveFlag', action='store_true',
                            help='Recursive into sub-directories.')
        parser.add_argument('-c', dest='checkFlag', action='store_true',
                            help='Check checksums against files.')

        parser.add_argument('files', nargs='+', metavar='file|file.md5',
                            help='File to checksum or ".md5" checksum file.')

        self._args = parser.parse_args(args)


class Md5sum(object):
    """
    Md5sum class
    """

    def __init__(self, options):
        if options.get_check_flag():
            self._check(options.get_files())
        else:
            self._calc(options, options.get_files())

    def _calc(self, options, files):
        for file in files:
            if os.path.isdir(file):
                if not os.path.islink(file) and options.get_recursive_flag():
                    try:
                        self._calc(options,
                                   sorted([os.path.join(file, x) for x in os.listdir(file)]))
                    except PermissionError:
                        raise SystemExit(sys.argv[0] + ': Cannot open "' + file + '" directory.')
            elif os.path.isfile(file):
                md5sum = self._md5sum(file)
                if not md5sum:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')
                print(md5sum, file, sep='  ')

    def _check(self, files):
        found = []
        nfiles = 0
        nfail = 0
        nmiss = 0
        for md5file in files:
            if not os.path.isfile(md5file):
                raise SystemExit(sys.argv[0] + ': Cannot find "' + md5file + '" md5sum file.')
            else:
                try:
                    with open(md5file, errors='replace') as ifile:
                        for line in ifile:
                            md5sum = line[:32]
                            file = line.rstrip()[34:]
                            if len(md5sum) == 32 and file:
                                found.append(file)
                                nfiles += 1
                                test = self._md5sum(file)
                                if not test:
                                    print(file, '# FAILED open or read')
                                    nmiss += 1
                                elif test != md5sum:
                                    print(file, '# FAILED checksum')
                                    nfail += 1
                except IOError:
                    raise SystemExit(sys.argv[0] + ': Cannot read "' + md5file + '" md5sum file.')
        if nmiss > 0:
            print('md5: Cannot find', nmiss, 'of', nfiles, 'listed files.')
        if nfail > 0:
            print('md5: Mismatch in', nfail, 'of', nfiles - nmiss, 'computed checksums.')

    def _md5sum(self, file):
        try:
            with open(file, 'rb') as ifile:
                md5 = hashlib.md5()
                while True:
                    chunk = ifile.read(131072)
                    if not chunk:
                        break
                    md5.update(chunk)
        except (IOError, TypeError):
            raise SystemExit(sys.argv[0] + ': Cannot read "' + file + '" file.')
        return md5.hexdigest()


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
            Md5sum(options)
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
